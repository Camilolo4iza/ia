import pytest
from unittest.mock import MagicMock
from src.agents.graph import VeterinaryAgentGraph
from src.agents.retriever_agent import RetrieverAgent
from src.agents.writer_agent import WriterAgent
from src.agents.state import VetAssistState

def test_retriever_agent_run():
    mock_rag = MagicMock()
    mock_rag.retrieve_context.return_value = [
        {"content": "Mock doc", "metadata": {"source_file": "test.txt", "topic": "test", "section": "test"}}
    ]
    
    agent = RetrieverAgent(mock_rag)
    # Mockear reformulación para no llamar a Groq
    agent.reformulate_query = MagicMock(return_value="opt query")
    
    state = {
        "query": "pregunta original",
        "retrieved_docs": [],
        "loop_count": 0
    }
    
    res = agent.run(state)
    assert res["loop_count"] == 1
    assert len(res["retrieved_docs"]) == 1
    assert res["retrieved_docs"][0]["content"] == "Mock doc"

def test_writer_agent_insufficient_info():
    agent = WriterAgent()
    
    # Mockear el LLM del redactor para simular info insuficiente
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "[INFORMACION_INSUFICIENTE] Falta dosis de meloxicam"
    agent._llm = mock_llm
    
    state = {
        "query": "pregunta",
        "retrieved_docs": [{"content": "Doc", "metadata": {"source_file": "a.txt", "section": "sec"}}],
        "loop_count": 1
    }
    
    res = agent.run(state)
    assert res["missing_info"] is True
    assert "Falta dosis de meloxicam" in res["missing_feedback"]
    assert "[INFORMACION_INSUFICIENTE]" in res["answer"]

def test_clinical_tools_node_runs_dose_calculator():
    graph = VeterinaryAgentGraph.__new__(VeterinaryAgentGraph)
    state = {
        "query": "Calcula la dosis de meloxicam",
        "patient_info": {"especie": "Perro", "peso": 10},
        "tool_outputs": []
    }

    res = graph._run_clinical_tools(state)

    assert len(res["tool_outputs"]) == 1
    assert "calcular_dosis" in res["tool_outputs"][0]
    assert "Meloxicam" in res["tool_outputs"][0]

def test_writer_agent_accepts_tool_outputs_without_docs():
    agent = WriterAgent()
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "Dosis calculada con apoyo MCP. [Fuente: MCP calcular_dosis]"
    agent._llm = mock_llm

    state = {
        "query": "Calcula la dosis de meloxicam",
        "retrieved_docs": [],
        "tool_outputs": ["[Herramienta MCP: calcular_dosis]\nDosis calculada"],
        "loop_count": 1
    }

    res = agent.run(state)

    assert res["missing_info"] is False
    assert "MCP herramientas clínicas" in res["sources"]
    assert "Dosis calculada" in res["answer"]
