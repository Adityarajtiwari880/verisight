"""
VeriSight MCP - Automated Comprehensive MCP Tool Test Suite
Validates 100% of exposed Model Context Protocol (MCP) tools by name.
Verifies readOnlyHint, destructiveHint, idempotentHint, and openWorldHint compliance.
"""

import os
import sys
import json
import unittest

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from mcp_server import MCP_TOOLS_MANIFEST, handle_json_rpc
from main import mcp_agent_callback

class TestVeriSightMCPTools(unittest.TestCase):
    """Rigorous unit and contract tests for all 10 VeriSight MCP forensic tools."""

    def test_mcp_manifest_hints_and_schema(self):
        """Verify all 10 tools declare required quality hints (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)."""
        self.assertEqual(len(MCP_TOOLS_MANIFEST), 10, "Expected exactly 10 registered MCP tools")
        
        required_hints = ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]
        
        for tool in MCP_TOOLS_MANIFEST:
            tool_name = tool.get("name")
            self.assertTrue(tool_name, "Tool must have a valid non-empty name")
            self.assertTrue(tool.get("description"), f"Tool {tool_name} missing description")
            self.assertIn("inputSchema", tool, f"Tool {tool_name} missing inputSchema")
            
            # Verify root-level hints
            for hint in required_hints:
                self.assertIn(hint, tool, f"Tool {tool_name} missing required hint '{hint}'")
                self.assertIsInstance(tool[hint], bool, f"Hint '{hint}' in {tool_name} must be a boolean")
                
            # Verify annotations sub-dictionary for MCP 2024-11-05 standard
            self.assertIn("annotations", tool, f"Tool {tool_name} missing annotations object")
            for hint in required_hints:
                self.assertIn(hint, tool["annotations"], f"Tool {tool_name} annotations missing '{hint}'")
                self.assertIsInstance(tool["annotations"][hint], bool)

    def test_verisight_inspect_claim(self):
        """Test tool: verisight_inspect_claim"""
        res = mcp_agent_callback("verisight_inspect_claim", {"preset": "genuine", "claim_id": "TEST-CLAIM-01"})
        self.assertIn("verdict", res)
        self.assertIn("tamper_probability", res)
        self.assertIn("action_taken", res)

    def test_verisight_active_clahe(self):
        """Test tool: verisight_active_clahe"""
        res = mcp_agent_callback("verisight_active_clahe", {"clip_limit": 3.0, "tile_grid_size": 8})
        self.assertEqual(res.get("status"), "success")
        self.assertIn("metrics", res)

    def test_verisight_sweep_jpeg_ghosts(self):
        """Test tool: verisight_sweep_jpeg_ghosts"""
        res = mcp_agent_callback("verisight_sweep_jpeg_ghosts", {
            "roi_bounding_box": [142, 92, 100, 100],
            "min_quality": 60,
            "max_quality": 80,
            "step": 10
        })
        self.assertEqual(res.get("status"), "success")
        self.assertIn("min_diff", res)

    def test_verisight_azimuthal_fourier_probe(self):
        """Test tool: verisight_azimuthal_fourier_probe"""
        res = mcp_agent_callback("verisight_azimuthal_fourier_probe", {"roi_bounding_box": [50, 50, 80, 80]})
        self.assertEqual(res.get("status"), "success")
        self.assertIn("dft_score", res)

    def test_verisight_sensor_noise_prnu(self):
        """Test tool: verisight_sensor_noise_prnu"""
        res = mcp_agent_callback("verisight_sensor_noise_prnu", {"roi_bounding_box": [50, 50, 80, 80]})
        self.assertEqual(res.get("status"), "success")
        self.assertIn("noise_diff", res)

    def test_verisight_perceptual_hash(self):
        """Test tool: verisight_perceptual_hash"""
        res = mcp_agent_callback("verisight_perceptual_hash", {"max_hamming_distance": 5})
        self.assertIn("phash_hex", res)

    def test_verisight_micro_roi_seam_check(self):
        """Test tool: verisight_micro_roi_seam_check"""
        res = mcp_agent_callback("verisight_micro_roi_seam_check", {"roi_bounding_box": [50, 50, 80, 80]})
        self.assertIn("seam_discontinuity_index", res)

    def test_verisight_cloud_ledger_audit(self):
        """Test tool: verisight_cloud_ledger_audit"""
        res = mcp_agent_callback("verisight_cloud_ledger_audit", {"limit": 3})
        self.assertIsInstance(res, list)

    def test_verisight_recapture_pad_analysis(self):
        """Test tool: verisight_recapture_pad_analysis"""
        res = mcp_agent_callback("verisight_recapture_pad_analysis", {"claim_type": "Auto Insurance Claim"})
        self.assertIn("is_recapture_attack", res)

    def test_verisight_verify_vehicle_damage(self):
        """Test tool: verisight_verify_vehicle_damage"""
        res = mcp_agent_callback("verisight_verify_vehicle_damage", {"min_damage_threshold": 20.0})
        self.assertIn("damage_verified", res)

    def test_json_rpc_dispatcher_tools_list(self):
        """Test JSON-RPC 2.0 tools/list request."""
        payload = {"jsonrpc": "2.0", "id": 42, "method": "tools/list", "params": {}}
        response = handle_json_rpc(payload, mcp_agent_callback)
        self.assertEqual(response.get("id"), 42)
        tools = response["result"]["tools"]
        self.assertEqual(len(tools), 10)

    def test_json_rpc_dispatcher_tools_call(self):
        """Test JSON-RPC 2.0 tools/call request for verisight_perceptual_hash."""
        payload = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "verisight_perceptual_hash",
                "arguments": {}
            }
        }
        response = handle_json_rpc(payload, mcp_agent_callback)
        self.assertEqual(response.get("id"), 101)
        self.assertFalse(response["result"]["isError"])
        self.assertTrue(len(response["result"]["content"]) > 0)

if __name__ == "__main__":
    unittest.main()
