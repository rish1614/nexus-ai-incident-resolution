import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin, Vector
from app.models.enums import KnowledgeSourceType

if TYPE_CHECKING:
    pass

# Embedding dimension is fixed at the schema level. 1536 matches common
# OpenAI-family embedding models; if Phase 3 selects a different embedding
# model this constant (and a migration) changes with it — see
# docs/rag-design.md once Phase 3 is implemented.
EMBEDDING_DIM = 1536


class KnowledgeDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A source document in the knowledge base (a runbook, a service doc, a
    past incident record, etc). Chunked and embedded by the Phase 3
    ingestion pipeline into `KnowledgeChunk` rows.
    """

    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    source_type: Mapped[KnowledgeSourceType] = mapped_column(
        Enum(KnowledgeSourceType, name="knowledge_source_type").with_variant(String(30), "sqlite"),
        nullable=False,
        index=True,
    )
    service: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    environment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_content: Mapped[str] = mapped_column(Text(), nullable=False)

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<KnowledgeDocument {self.title} ({self.source_type})>"


class KnowledgeChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A single embedded chunk of a KnowledgeDocument. `chunk_index` preserves
    original document order for citation display. `embedding` is a pgvector
    column in Postgres (see app.models.base.Vector for the SQLite-test
    fallback).
    """

    __tablename__ = "knowledge_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")

    chunk_index: Mapped[int] = mapped_column(Integer(), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<KnowledgeChunk {self.document_id}#{self.chunk_index}>"
