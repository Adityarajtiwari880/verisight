"""
VeriSight MCP - Sub-3ms Physical Image Forensics & Multi-Spectral Fraud Detection
"""
from backend.agent import forensic_agent, ForensicAgent
from backend.aws_adapter import aws_adapter, AWSCloudAdapter
from backend import __version__

__all__ = ["forensic_agent", "ForensicAgent", "aws_adapter", "AWSCloudAdapter", "__version__"]
