"""
VeriSight MCP - Official Model Context Protocol (MCP) Tool Integration
Exposes standard MCP tool definitions and JSON-RPC dispatchers, enabling LLMs
(Claude Desktop, Cursor, ChatGPT, LangChain) to autonomously invoke OpenCV 5 forensic tools.
Includes full quality annotations conforming to Anthropic MCP & OpenAI directory specifications.
"""

from typing import Dict, Any, List, Optional

MCP_TOOLS_MANIFEST: List[Dict[str, Any]] = [
    {
        "name": "verisight_inspect_claim",
        "description": "Orchestrates full multi-spectral OpenCV 5 forensic triage on a claim image (CLAHE, ELA, Fourier 2D DFT, PRNU noise, and Chrominance).",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_id": {"type": "string", "description": "Unique refund or claim identifier"},
                "claim_type": {"type": "string", "description": "Category (e.g. Quick-Commerce produce, Auto insurance, Electronics)"},
                "confidence_threshold": {"type": "number", "description": "Tamper risk rejection threshold (default: 70.0)"}
            },
            "required": ["claim_id"]
        }
    },
    {
        "name": "verisight_active_clahe",
        "description": "Photometric active perception tool using OpenCV 5 cv2.createCLAHE in LAB color space to restore underexposed frames.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "clip_limit": {"type": "number", "description": "Contrast limit for CLAHE (default: 3.5)"},
                "tile_grid_size": {"type": "integer", "description": "Grid tile dimension (default: 8)"}
            }
        }
    },
    {
        "name": "verisight_sweep_jpeg_ghosts",
        "description": "Multi-Q JPEG Ghost Sweeper. Detects spliced inpainting patches resaved at different compression qualities.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_quality": {"type": "integer", "description": "Starting JPEG quality factor (default: 60)"},
                "max_quality": {"type": "integer", "description": "Ending JPEG quality factor (default: 96)"},
                "step": {"type": "integer", "description": "Step interval (default: 4)"}
            }
        }
    },
    {
        "name": "verisight_azimuthal_fourier_probe",
        "description": "Azimuthal 2D Fast Fourier Transform (cv2.dft) probe to detect periodic upsampling grids from generative diffusion models.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "roi_bounding_box": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "[x, y, width, height] coordinates of suspect region"
                }
            },
            "required": ["roi_bounding_box"]
        }
    },
    {
        "name": "verisight_sensor_noise_prnu",
        "description": "Extracts high-pass sensor noise residual (R = I - cv2.medianBlur(I, 3)) and detects local PRNU variance anomalies.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "roi_bounding_box": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "[x, y, width, height] coordinates of suspect region"
                }
            },
            "required": ["roi_bounding_box"]
        }
    },
    {
        "name": "verisight_perceptual_hash",
        "description": "Computes a 64-bit 2D-DCT frequency perceptual hash (pHash) and scans DynamoDB for duplicate photo reuse and Sybil refund rings.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_hamming_distance": {"type": "integer", "description": "Maximum bit divergence threshold (default: 5)"}
            }
        }
    },
    {
        "name": "verisight_micro_roi_seam_check",
        "description": "Autonomous micro-investigation loop. Upscales suspect ROI 2x using Lanczos interpolation and measures boundary seam Laplacian discontinuity.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "roi_bounding_box": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "[x, y, width, height] suspect coordinates"
                }
            },
            "required": ["roi_bounding_box"]
        }
    },
    {
        "name": "verisight_cloud_ledger_audit",
        "description": "Queries the immutable AWS DynamoDB tamper ledger and retrieves S3 forensic evidence bundles.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of recent audit records to retrieve (default: 10)"}
            }
        }
    },
    {
        "name": "verisight_recapture_pad_analysis",
        "description": "Evaluates Presentation Attack Detection (PAD) conforming to ISO/IEC 30107-3: planar card boundaries, printed typography strips, 2D-DFT halftone/Moiré spectral resonance, and diffuse print gamut.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_type": {"type": "string", "description": "Domain of claim (e.g. Auto insurance, Fresh produce, Delivery package)"}
            }
        }
    },
    {
        "name": "verisight_verify_vehicle_damage",
        "description": "Evaluates physical collision damage presence on vehicle panels: localized Laplacian curvature deformation, paint scratch contours, and impact concentration ratios.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_damage_threshold": {"type": "number", "description": "Minimum damage score required to verify physical collision (default: 25.0)"}
            }
        }
    }
]

def handle_json_rpc(payload: Dict[str, Any], agent_pipeline_callback) -> Optional[Dict[str, Any]]:
    """
    Standard JSON-RPC 2.0 dispatcher for Model Context Protocol (MCP) clients.
    Handles initialize handshake, tool discovery, and execution.
    """
    req_id = payload.get("id", 1)
    method = payload.get("method", "")
    params = payload.get("params", {})
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "verisight-mcp-engine",
                    "version": "2.2.0"
                }
            }
        }

    elif method in ["notifications/initialized", "initialized"]:
        return None  # Standard JSON-RPC 2.0 notification: no response required
        
    elif method in ["tools/list", "mcp/tools"]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS_MANIFEST,
                "protocol_version": "2024-11-05",
                "server_info": {
                    "name": "verisight-mcp-engine",
                    "version": "2.2.0",
                    "capabilities": {"tools": True, "resources": False, "prompts": False}
                }
            }
        }
        
    elif method in ["tools/call", "mcp/execute"]:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Dispatch to registered agent handler
        tool_result = agent_pipeline_callback(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(tool_result)
                    }
                ],
                "isError": False
            }
        }
        
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found."
            }
        }

def run_stdio_server(agent_pipeline_callback=None):
    """
    Standard I/O (stdio) event loop for Model Context Protocol (MCP) clients
    like Claude Desktop, Cursor, Windsurf, and Smithery.
    """
    import sys
    import json
    
    if agent_pipeline_callback is None:
        from main import mcp_agent_callback
        agent_pipeline_callback = mcp_agent_callback

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            response = handle_json_rpc(payload, agent_pipeline_callback)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error or exception: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_response) + "\n")
            sys.stdout.flush()
