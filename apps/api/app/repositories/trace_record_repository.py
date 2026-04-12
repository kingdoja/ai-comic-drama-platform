from typing import List, Optional, Set, Dict, Any
from uuid import UUID
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import TraceRecordModel


class TraceRecordRepository:
    """
    Repository for TraceRecord database operations.
    
    Provides operations for creating and querying trace records, including
    recursive lineage queries to build complete data flow graphs.
    
    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    
    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        project_id: UUID,
        episode_id: UUID,
        event_type: str,
        source_type: str,
        source_id: UUID,
        target_type: str,
        target_id: UUID,
        metadata_jsonb: Optional[dict] = None,
    ) -> TraceRecordModel:
        """
        Create a new trace record.
        
        Requirements: 7.1
        
        Args:
            project_id: Project UUID
            episode_id: Episode UUID
            event_type: Event type (stage_execution, asset_generation, document_creation, transformation)
            source_type: Source entity type (document, shot, asset, stage_task)
            source_id: Source entity UUID
            target_type: Target entity type (document, shot, asset, stage_task)
            target_id: Target entity UUID
            metadata_jsonb: Optional metadata dictionary
            
        Returns:
            Created TraceRecordModel instance
        """
        trace_record = TraceRecordModel(
            project_id=project_id,
            episode_id=episode_id,
            event_type=event_type,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            metadata_jsonb=metadata_jsonb or {},
        )
        
        self.db.add(trace_record)
        self.db.flush()
        self.db.refresh(trace_record)
        
        return trace_record
    
    def get_by_episode(
        self,
        episode_id: UUID,
        limit: int = 1000
    ) -> List[TraceRecordModel]:
        """
        Get all trace records for a specific episode.
        
        Requirements: 7.1
        
        Args:
            episode_id: Episode UUID
            limit: Maximum number of records to return
            
        Returns:
            List of TraceRecordModel instances ordered by event_timestamp ascending
        """
        stmt = (
            select(TraceRecordModel)
            .where(TraceRecordModel.episode_id == episode_id)
            .order_by(TraceRecordModel.event_timestamp.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def get_by_source(
        self,
        source_type: str,
        source_id: UUID,
        limit: int = 100
    ) -> List[TraceRecordModel]:
        """
        Get trace records by source entity.
        
        Requirements: 7.3
        
        Args:
            source_type: Source entity type (document, shot, asset, stage_task)
            source_id: Source entity UUID
            limit: Maximum number of records to return
            
        Returns:
            List of TraceRecordModel instances ordered by event_timestamp ascending
        """
        stmt = (
            select(TraceRecordModel)
            .where(
                TraceRecordModel.source_type == source_type,
                TraceRecordModel.source_id == source_id
            )
            .order_by(TraceRecordModel.event_timestamp.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def get_by_target(
        self,
        target_type: str,
        target_id: UUID,
        limit: int = 100
    ) -> List[TraceRecordModel]:
        """
        Get trace records by target entity.
        
        Requirements: 7.3
        
        Args:
            target_type: Target entity type (document, shot, asset, stage_task)
            target_id: Target entity UUID
            limit: Maximum number of records to return
            
        Returns:
            List of TraceRecordModel instances ordered by event_timestamp ascending
        """
        stmt = (
            select(TraceRecordModel)
            .where(
                TraceRecordModel.target_type == target_type,
                TraceRecordModel.target_id == target_id
            )
            .order_by(TraceRecordModel.event_timestamp.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def get_lineage(
        self,
        entity_type: str,
        entity_id: UUID,
        direction: str = "backward",
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Get lineage graph for an entity with recursive traversal.
        
        Requirements: 7.2, 7.3, 7.4
        
        Args:
            entity_type: Entity type (document, shot, asset, stage_task)
            entity_id: Entity UUID
            direction: Query direction:
                - "backward" (upstream): Find sources that led to this entity
                - "forward" (downstream): Find targets derived from this entity
                - "both": Find both upstream and downstream entities
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Dictionary containing:
                - nodes: List of unique entities in the lineage graph
                - edges: List of trace records connecting the entities
                - root: The starting entity
        """
        visited_nodes: Set[tuple] = set()
        all_edges: List[TraceRecordModel] = []
        
        # Start recursive traversal
        if direction in ("backward", "both"):
            self._traverse_backward(
                entity_type, entity_id, visited_nodes, all_edges, max_depth
            )
        
        if direction in ("forward", "both"):
            self._traverse_forward(
                entity_type, entity_id, visited_nodes, all_edges, max_depth
            )
        
        # Build unique nodes list
        nodes = [
            {"type": node_type, "id": str(node_id)}
            for node_type, node_id in visited_nodes
        ]
        
        # Build edges list with serializable data
        edges = [
            {
                "id": str(edge.id),
                "event_type": edge.event_type,
                "source_type": edge.source_type,
                "source_id": str(edge.source_id),
                "target_type": edge.target_type,
                "target_id": str(edge.target_id),
                "event_timestamp": edge.event_timestamp.isoformat() if edge.event_timestamp else None,
                "metadata": edge.metadata_jsonb
            }
            for edge in all_edges
        ]
        
        return {
            "root": {"type": entity_type, "id": str(entity_id)},
            "nodes": nodes,
            "edges": edges,
            "direction": direction
        }
    
    def _traverse_backward(
        self,
        entity_type: str,
        entity_id: UUID,
        visited_nodes: Set[tuple],
        all_edges: List[TraceRecordModel],
        remaining_depth: int
    ) -> None:
        """
        Recursively traverse backward (upstream) to find source entities.
        
        Args:
            entity_type: Current entity type
            entity_id: Current entity UUID
            visited_nodes: Set of visited (type, id) tuples to prevent cycles
            all_edges: List to accumulate all trace records
            remaining_depth: Remaining recursion depth
        """
        if remaining_depth <= 0:
            return
        
        node_key = (entity_type, entity_id)
        if node_key in visited_nodes:
            return
        
        visited_nodes.add(node_key)
        
        # Find all trace records where this entity is the target
        stmt = select(TraceRecordModel).where(
            TraceRecordModel.target_type == entity_type,
            TraceRecordModel.target_id == entity_id
        )
        
        upstream_records = list(self.db.scalars(stmt).all())
        
        for record in upstream_records:
            if record not in all_edges:
                all_edges.append(record)
            
            # Recursively traverse to source
            self._traverse_backward(
                record.source_type,
                record.source_id,
                visited_nodes,
                all_edges,
                remaining_depth - 1
            )
    
    def _traverse_forward(
        self,
        entity_type: str,
        entity_id: UUID,
        visited_nodes: Set[tuple],
        all_edges: List[TraceRecordModel],
        remaining_depth: int
    ) -> None:
        """
        Recursively traverse forward (downstream) to find target entities.
        
        Args:
            entity_type: Current entity type
            entity_id: Current entity UUID
            visited_nodes: Set of visited (type, id) tuples to prevent cycles
            all_edges: List to accumulate all trace records
            remaining_depth: Remaining recursion depth
        """
        if remaining_depth <= 0:
            return
        
        node_key = (entity_type, entity_id)
        if node_key in visited_nodes:
            return
        
        visited_nodes.add(node_key)
        
        # Find all trace records where this entity is the source
        stmt = select(TraceRecordModel).where(
            TraceRecordModel.source_type == entity_type,
            TraceRecordModel.source_id == entity_id
        )
        
        downstream_records = list(self.db.scalars(stmt).all())
        
        for record in downstream_records:
            if record not in all_edges:
                all_edges.append(record)
            
            # Recursively traverse to target
            self._traverse_forward(
                record.target_type,
                record.target_id,
                visited_nodes,
                all_edges,
                remaining_depth - 1
            )
