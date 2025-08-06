"""
Sanctions Data Manager

Handles integration with various sanctions data sources including OFAC, UN, EU,
and crypto-specific sanctions lists. Provides data caching, normalization,
and real-time updates.
"""

import os
import json
import xml.etree.ElementTree as ET
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import hashlib
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class SanctionsEntity:
    """Standardized sanctions entity data structure"""
    uid: str  # Unique identifier
    name: str
    entity_type: str  # 'individual', 'entity', 'vessel', 'aircraft'
    program: str  # Sanctions program
    source_list: str  # OFAC_SDN, UN_SC, etc.
    aliases: List[str]
    addresses: List[str]
    identifiers: List[Dict[str, str]]  # passports, tax IDs, etc.
    dates_of_birth: List[str]
    places_of_birth: List[str]
    nationalities: List[str]
    remarks: str
    last_updated: str
    crypto_addresses: List[str]  # For crypto-specific sanctions

class SanctionsDataManager:
    """
    Manages sanctions data from multiple sources with caching and real-time updates
    """
    
    def __init__(self, data_dir: str = "data/sanctions"):
        """Initialize the sanctions data manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for cached sanctions data
        self.db_path = self.data_dir / "sanctions.db"
        self._init_database()
        
        # Data source configurations
        self.data_sources = {
            'OFAC_SDN': {
                'url': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
                'format': 'xml',
                'parser': self._parse_ofac_sdn,
                'update_frequency': 24  # hours
            },
            'OFAC_CONS': {
                'url': 'https://www.treasury.gov/ofac/downloads/cons.xml',
                'format': 'xml',
                'parser': self._parse_ofac_cons,
                'update_frequency': 24
            },
            'OFAC_CRYPTO': {
                'url': 'https://home.treasury.gov/system/files/126/digital_currency_addresses.json',
                'format': 'json',
                'parser': self._parse_ofac_crypto,
                'update_frequency': 6
            },
            'UN_SC': {
                'url': 'https://scsanctions.un.org/resources/xml/en/consolidated.xml',
                'format': 'xml',
                'parser': self._parse_un_sanctions,
                'update_frequency': 24
            },
            'EU_SANCTIONS': {
                'url': 'https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content',
                'format': 'xml',
                'parser': self._parse_eu_sanctions,
                'update_frequency': 24
            },
            'UK_HMT': {
                'url': 'https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.json',
                'format': 'json',
                'parser': self._parse_uk_sanctions,
                'update_frequency': 24
            }
        }
        
        # Cache settings
        self.cache_duration = 3600  # 1 hour default
        self.last_update_check = {}
        
    def _init_database(self):
        """Initialize SQLite database for sanctions data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sanctions_entities (
                    uid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT,
                    program TEXT,
                    source_list TEXT,
                    aliases TEXT,  -- JSON array
                    addresses TEXT,  -- JSON array
                    identifiers TEXT,  -- JSON array
                    dates_of_birth TEXT,  -- JSON array
                    places_of_birth TEXT,  -- JSON array
                    nationalities TEXT,  -- JSON array
                    remarks TEXT,
                    last_updated TEXT,
                    crypto_addresses TEXT,  -- JSON array
                    search_text TEXT  -- For full-text search
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_name ON sanctions_entities(name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source ON sanctions_entities(source_list)
            """)
            
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS sanctions_fts USING fts5(
                    uid, name, aliases, search_text, content='sanctions_entities'
                )
            """)
            
            conn.commit()
    
    async def update_all_sources(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Update all sanctions data sources
        
        Args:
            force_update: Force update even if cache is valid
            
        Returns:
            Update results for each source
        """
        results = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, config in self.data_sources.items():
                if force_update or self._needs_update(source_name, config['update_frequency']):
                    task = self._update_source(session, source_name, config)
                    tasks.append(task)
            
            if tasks:
                source_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(source_results):
                    source_name = list(self.data_sources.keys())[i]
                    if isinstance(result, Exception):
                        results[source_name] = {'success': False, 'error': str(result)}
                    else:
                        results[source_name] = result
        
        return results
    
    async def _update_source(self, session: aiohttp.ClientSession, 
                           source_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update a single sanctions data source"""
        try:
            logger.info(f"Updating sanctions data from {source_name}")
            
            # Download data
            async with session.get(config['url'], timeout=300) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                content = await response.text()
            
            # Parse data using source-specific parser
            entities = config['parser'](content, source_name)
            
            # Store in database
            stored_count = self._store_entities(entities, source_name)
            
            # Update last check time
            self.last_update_check[source_name] = datetime.now()
            
            logger.info(f"Updated {source_name}: {stored_count} entities stored")
            
            return {
                'success': True,
                'entities_count': stored_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update {source_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _needs_update(self, source_name: str, update_frequency_hours: int) -> bool:
        """Check if a data source needs updating"""
        if source_name not in self.last_update_check:
            return True
        
        last_check = self.last_update_check[source_name]
        time_since_update = datetime.now() - last_check
        
        return time_since_update.total_seconds() > (update_frequency_hours * 3600)
    
    def _store_entities(self, entities: List[SanctionsEntity], source_name: str) -> int:
        """Store sanctions entities in the database"""
        with sqlite3.connect(self.db_path) as conn:
            # Delete existing entities from this source
            conn.execute("DELETE FROM sanctions_entities WHERE source_list = ?", (source_name,))
            
            # Insert new entities
            stored_count = 0
            for entity in entities:
                try:
                    # Create search text for full-text search
                    search_text = f"{entity.name} {' '.join(entity.aliases)} {entity.remarks}"
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO sanctions_entities 
                        (uid, name, entity_type, program, source_list, aliases, addresses,
                         identifiers, dates_of_birth, places_of_birth, nationalities,
                         remarks, last_updated, crypto_addresses, search_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entity.uid,
                        entity.name,
                        entity.entity_type,
                        entity.program,
                        entity.source_list,
                        json.dumps(entity.aliases),
                        json.dumps(entity.addresses),
                        json.dumps(entity.identifiers),
                        json.dumps(entity.dates_of_birth),
                        json.dumps(entity.places_of_birth),
                        json.dumps(entity.nationalities),
                        entity.remarks,
                        entity.last_updated,
                        json.dumps(entity.crypto_addresses),
                        search_text
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing entity {entity.name}: {e}")
            
            # Update FTS index
            conn.execute("INSERT INTO sanctions_fts(sanctions_fts) VALUES('rebuild')")
            conn.commit()
            
            return stored_count
    
    def search_entities(self, query: str, source_lists: Optional[List[str]] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search sanctions entities
        
        Args:
            query: Search query
            source_lists: Specific source lists to search
            limit: Maximum results to return
            
        Returns:
            List of matching entities
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build query
            if source_lists:
                source_filter = " AND source_list IN ({})".format(
                    ','.join('?' * len(source_lists))
                )
                params = [query] + source_lists + [limit]
            else:
                source_filter = ""
                params = [query, limit]
            
            # Use full-text search
            sql = f"""
                SELECT e.* FROM sanctions_entities e
                JOIN sanctions_fts fts ON e.uid = fts.uid
                WHERE fts MATCH ?{source_filter}
                ORDER BY rank
                LIMIT ?
            """
            
            cursor = conn.execute(sql, params)
            results = []
            
            for row in cursor.fetchall():
                entity_dict = dict(row)
                # Parse JSON fields
                for field in ['aliases', 'addresses', 'identifiers', 'dates_of_birth',
                             'places_of_birth', 'nationalities', 'crypto_addresses']:
                    if entity_dict[field]:
                        entity_dict[field] = json.loads(entity_dict[field])
                    else:
                        entity_dict[field] = []
                
                results.append(entity_dict)
            
            return results
    
    def get_entity_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a specific entity by UID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute(
                "SELECT * FROM sanctions_entities WHERE uid = ?", (uid,)
            )
            row = cursor.fetchone()
            
            if row:
                entity_dict = dict(row)
                # Parse JSON fields
                for field in ['aliases', 'addresses', 'identifiers', 'dates_of_birth',
                             'places_of_birth', 'nationalities', 'crypto_addresses']:
                    if entity_dict[field]:
                        entity_dict[field] = json.loads(entity_dict[field])
                    else:
                        entity_dict[field] = []
                
                return entity_dict
            
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Total entities
            cursor = conn.execute("SELECT COUNT(*) FROM sanctions_entities")
            total_entities = cursor.fetchone()[0]
            
            # Entities by source
            cursor = conn.execute("""
                SELECT source_list, COUNT(*) as count 
                FROM sanctions_entities 
                GROUP BY source_list
            """)
            by_source = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Entities by type
            cursor = conn.execute("""
                SELECT entity_type, COUNT(*) as count 
                FROM sanctions_entities 
                GROUP BY entity_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Last update times
            last_updates = {
                source: check_time.isoformat() if check_time else None
                for source, check_time in self.last_update_check.items()
            }
            
            return {
                'total_entities': total_entities,
                'entities_by_source': by_source,
                'entities_by_type': by_type,
                'last_updates': last_updates,
                'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
            }
    
    # Data source parsers
    
    def _parse_ofac_sdn(self, xml_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse OFAC SDN XML data"""
        entities = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for sdn_entry in root.findall('.//sdnEntry'):
                uid = sdn_entry.get('uid', '')
                
                # Basic info
                first_name = sdn_entry.findtext('firstName', '')
                last_name = sdn_entry.findtext('lastName', '')
                name = f"{first_name} {last_name}".strip()
                if not name:
                    name = sdn_entry.findtext('title', 'Unknown')
                
                entity_type = sdn_entry.findtext('sdnType', 'unknown')
                program = sdn_entry.findtext('programList/program', '')
                remarks = sdn_entry.findtext('remarks', '')
                
                # Aliases
                aliases = []
                for aka in sdn_entry.findall('.//aka'):
                    aka_type = aka.get('type', '')
                    category = aka.get('category', '')
                    first = aka.findtext('firstName', '')
                    last = aka.findtext('lastName', '')
                    alias_name = f"{first} {last}".strip()
                    if alias_name and alias_name != name:
                        aliases.append(alias_name)
                
                # Addresses
                addresses = []
                for address in sdn_entry.findall('.//address'):
                    addr_parts = []
                    for field in ['address1', 'address2', 'city', 'stateOrProvince', 'country']:
                        value = address.findtext(field, '')
                        if value:
                            addr_parts.append(value)
                    if addr_parts:
                        addresses.append(', '.join(addr_parts))
                
                # Identifiers
                identifiers = []
                for id_elem in sdn_entry.findall('.//id'):
                    id_type = id_elem.get('idType', '')
                    id_number = id_elem.get('idNumber', '')
                    if id_type and id_number:
                        identifiers.append({'type': id_type, 'number': id_number})
                
                # Dates and places of birth
                dates_of_birth = []
                places_of_birth = []
                for dob in sdn_entry.findall('.//dateOfBirth'):
                    date_value = dob.get('dateOfBirth', '')
                    if date_value:
                        dates_of_birth.append(date_value)
                
                for pob in sdn_entry.findall('.//placeOfBirth'):
                    place_value = pob.get('placeOfBirth', '')
                    if place_value:
                        places_of_birth.append(place_value)
                
                # Nationalities
                nationalities = []
                for nationality in sdn_entry.findall('.//nationality'):
                    country = nationality.get('country', '')
                    if country:
                        nationalities.append(country)
                
                entity = SanctionsEntity(
                    uid=f"{source_name}_{uid}",
                    name=name,
                    entity_type=entity_type,
                    program=program,
                    source_list=source_name,
                    aliases=aliases,
                    addresses=addresses,
                    identifiers=identifiers,
                    dates_of_birth=dates_of_birth,
                    places_of_birth=places_of_birth,
                    nationalities=nationalities,
                    remarks=remarks,
                    last_updated=datetime.now().isoformat(),
                    crypto_addresses=[]
                )
                
                entities.append(entity)
        
        except ET.ParseError as e:
            logger.error(f"Error parsing OFAC SDN XML: {e}")
        
        return entities
    
    def _parse_ofac_cons(self, xml_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse OFAC Consolidated Sanctions List"""
        # Similar to SDN but different structure
        # Implementation would follow OFAC CONS XML format
        return []  # Placeholder
    
    def _parse_ofac_crypto(self, json_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse OFAC crypto addresses JSON"""
        entities = []
        
        try:
            data = json.loads(json_content)
            
            for entry in data.get('entries', []):
                # Extract crypto address info
                addresses = entry.get('addresses', [])
                entity_name = entry.get('name', 'Unknown Crypto Entity')
                
                for addr_info in addresses:
                    crypto_address = addr_info.get('address', '')
                    currency = addr_info.get('currency', '')
                    
                    if crypto_address:
                        uid = hashlib.md5(f"{source_name}_{crypto_address}".encode()).hexdigest()
                        
                        entity = SanctionsEntity(
                            uid=uid,
                            name=f"{entity_name} ({currency})",
                            entity_type='crypto_address',
                            program='OFAC_CRYPTO',
                            source_list=source_name,
                            aliases=[],
                            addresses=[],
                            identifiers=[{'type': 'crypto_address', 'number': crypto_address}],
                            dates_of_birth=[],
                            places_of_birth=[],
                            nationalities=[],
                            remarks=f"Sanctioned {currency} address",
                            last_updated=datetime.now().isoformat(),
                            crypto_addresses=[crypto_address]
                        )
                        
                        entities.append(entity)
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OFAC crypto JSON: {e}")
        
        return entities
    
    def _parse_un_sanctions(self, xml_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse UN Security Council sanctions XML"""
        # Implementation for UN sanctions format
        return []  # Placeholder
    
    def _parse_eu_sanctions(self, xml_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse EU sanctions XML"""
        # Implementation for EU sanctions format
        return []  # Placeholder
    
    def _parse_uk_sanctions(self, json_content: str, source_name: str) -> List[SanctionsEntity]:
        """Parse UK HMT sanctions JSON"""
        # Implementation for UK sanctions format
        return []  # Placeholder

# Convenience functions
def create_sanctions_manager(data_dir: str = "data/sanctions") -> SanctionsDataManager:
    """Create a sanctions data manager instance"""
    return SanctionsDataManager(data_dir)

async def update_sanctions_data(manager: SanctionsDataManager, force_update: bool = False) -> Dict[str, Any]:
    """Update all sanctions data sources"""
    return await manager.update_all_sources(force_update)

def search_sanctions(manager: SanctionsDataManager, query: str, 
                    source_lists: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Search sanctions entities"""
    return manager.search_entities(query, source_lists)