from autonomy import Agent, HttpServer, Model, Node, NodeDep, McpTool, McpClient
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from asyncio import gather, create_task
from typing import List, Dict
import json
import os
import time

app = FastAPI()

class FactCheckRequest(BaseModel):
    article: str

class FactCheckResponse(BaseModel):
    report: str
    status: str


async def extract_claims(node: Node, article: str) -> List[str]:
    """
    Extract factual claims from an article using a dedicated agent.
    """
    agent_name = f"claim_extractor_{int(time.time() * 1000)}"
    
    try:
        agent = await Agent.start(
            node=node,
            name=agent_name,
            instructions="""
            You are a claim extraction specialist. Your job is to analyze news articles 
            and identify specific factual claims that can be verified.
            
            For each article, extract claims that are:
            - Specific and verifiable (not opinions or predictions)
            - Important to the article's narrative
            - Factual statements (statistics, quotes, events, dates, etc.)
            
            Return your response as a JSON array of claim objects with this format:
            [
                {
                    "claim": "The exact claim text",
                    "type": "statistic|quote|event|date|fact",
                    "context": "Brief context from article"
                }
            ]
            
            Extract 3-10 claims depending on article length. Focus on the most important claims.
            """,
            model=Model("claude-sonnet-4-v1")
        )
        
        response = await agent.send(
            f"Extract verifiable claims from this article:\n\n{article}",
            timeout=60
        )
        
        # Parse the response to get claims
        response_text = response[-1].content.text
        
        # Try to extract JSON from the response
        try:
            # Look for JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                claims_data = json.loads(json_str)
                claims = [f"{c['claim']} (Context: {c.get('context', 'N/A')})" for c in claims_data]
            else:
                # Fallback: treat each line as a claim
                claims = [line.strip() for line in response_text.split('\n') 
                         if line.strip() and not line.strip().startswith('[') 
                         and not line.strip().startswith(']')]
        except:
            # If JSON parsing fails, split by lines
            claims = [line.strip() for line in response_text.split('\n') 
                     if line.strip() and len(line.strip()) > 20]
        
        return claims[:10]  # Limit to 10 claims
        
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return [f"Could not extract claims: {str(e)}"]
    finally:
        try:
            await Agent.stop(node, agent_name)
        except:
            pass


async def fact_check_claim(node: Node, claim: str, claim_idx: int) -> Dict[str, str]:
    """
    Fact-check a single claim using web search.
    """
    agent_name = f"fact_checker_{claim_idx}_{int(time.time() * 1000)}"
    
    try:
        agent = await Agent.start(
            node=node,
            name=agent_name,
            instructions="""
            You are a professional fact-checker. Your job is to verify claims using web search.
            
            For each claim:
            1. Use the brave_web_search tool to find relevant sources
            2. Analyze the credibility of sources
            3. Determine the claim's veracity
            4. Provide a clear assessment
            
            Your response should include:
            - Verdict: TRUE / FALSE / PARTIALLY TRUE / UNVERIFIABLE
            - Reasoning: Brief explanation of your assessment
            - Sources: List of URLs you used
            - Confidence: High / Medium / Low
            
            Be thorough but concise. Focus on credible sources like news organizations,
            academic institutions, and official websites.
            """,
            model=Model("claude-sonnet-4-v1"),
            tools=[McpTool("brave_search", "brave_web_search")]
        )
        
        response = await agent.send(
            f"Fact-check this claim:\n\n{claim}",
            timeout=90
        )
        
        result_text = response[-1].content.text
        
        return {
            "claim": claim,
            "result": result_text,
            "status": "completed"
        }
        
    except Exception as e:
        return {
            "claim": claim,
            "result": f"Error during fact-check: {str(e)}",
            "status": "error"
        }
    finally:
        try:
            await Agent.stop(node, agent_name)
        except:
            pass


async def generate_report(node: Node, article: str, fact_check_results: List[Dict]) -> str:
    """
    Generate a comprehensive fact-check report from all results.
    """
    agent_name = f"report_generator_{int(time.time() * 1000)}"
    
    try:
        agent = await Agent.start(
            node=node,
            name=agent_name,
            instructions="""
            You are a report writer specializing in fact-check reports. Create clear,
            professional reports that help news editors understand article credibility.
            
            Your report should include:
            1. Executive Summary (2-3 sentences on overall article credibility)
            2. Claim-by-Claim Analysis (for each claim, include verdict and key evidence)
            3. Overall Assessment (credibility rating and recommendations)
            4. Sources (list of all sources used)
            
            Format the report in clear markdown with proper headings and structure.
            Be objective and evidence-based. Highlight any red flags or concerns.
            """,
            model=Model("claude-sonnet-4-v1")
        )
        
        # Prepare the fact-check results summary
        results_summary = "\n\n".join([
            f"**Claim {i+1}:** {r['claim']}\n\n{r['result']}\n"
            for i, r in enumerate(fact_check_results)
        ])
        
        response = await agent.send(
            f"""Create a comprehensive fact-check report.

ORIGINAL ARTICLE:
{article[:1000]}{'...' if len(article) > 1000 else ''}

FACT-CHECK RESULTS:
{results_summary}

Please generate a professional fact-check report based on these findings.""",
            timeout=60
        )
        
        return response[-1].content.text
        
    except Exception as e:
        return f"Error generating report: {str(e)}"
    finally:
        try:
            await Agent.stop(node, agent_name)
        except:
            pass


@app.post("/api/fact-check", response_model=FactCheckResponse)
async def fact_check_article(request: FactCheckRequest, node: NodeDep):
    """
    Main endpoint to fact-check an article.
    """
    try:
        article = request.article
        
        if not article or len(article) < 50:
            raise HTTPException(status_code=400, detail="Article too short. Please provide a substantial article to fact-check.")
        
        # Step 1: Extract claims from the article
        claims = await extract_claims(node, article)
        
        if not claims or len(claims) == 0:
            raise HTTPException(status_code=400, detail="No verifiable claims found in the article.")
        
        # Step 2: Fact-check all claims in parallel
        fact_check_results = await gather(*[
            fact_check_claim(node, claim, i) 
            for i, claim in enumerate(claims)
        ])
        
        # Step 3: Generate comprehensive report
        report = await generate_report(node, article, fact_check_results)
        
        return FactCheckResponse(
            report=report,
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact-check failed: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/agents")
async def list_agents(node: NodeDep):
    """List all running agents."""
    try:
        # This is a placeholder - Autonomy handles agent listing internally
        return {"message": "Agent listing available via Autonomy API"}
    except Exception as e:
        return {"error": str(e)}


# Serve static files (must be last)
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="static")


# Start the node with MCP client for Brave Search
Node.start(
    http_server=HttpServer(app=app),
    mcp_clients=[
        McpClient(name="brave_search", address="http://localhost:8001/sse"),
    ],
)



