import os
from pydantic import BaseModel, Field
from typing import List
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool

# Our "Knowledge Base" of solutions
# This maps PROBLEM TYPES to a list of solutions
# --- PHASE 1: THE KNOWLEDGE BASE (DATABASE) ---
# This is our mock DB of expert knowledge for the hackathon.
# We are manually populating it based on the expert URS document.
# It maps "problem_domains" (bottlenecks) to proposed solutions.

SOLUTION_KNOWLEDGE_BASE = {
    "weighing": [
        {
            "solution_name": "Automated Weighing Station (URS APL01)",
            "description": "An automated or semi-automated station to replace manual weighing[cite: 515]. Handles weighing compounds from 0.2mg - 100g [cite: 527] and supports one-to-many, one-to-one, and many-to-one workflows[cite: 541].",
            "example_vendors": ["(Vendor research needed)"],
            "avg_budget": "$70,000 - $200,000",
            "key_requirements": [
                "Handle solids (powders, flakes, etc) and liquids [cite: 529]",
                "Read/produce barcodes [cite: 533]",
                "Throughput: 84+ compounds/day [cite: 535]",
                "Import/export worklists (csv, xml) [cite: 539]"
            ]
        },
        {
            "solution_name": "Manual Computer-Assisted Weighing Station (URS APL02)",
            "description": "A simpler station that assists a human user[cite: 548, 571]. It displays target weights, automatically records the weight, and steps through a compound list[cite: 585].",
            "example_vendors": ["(Vendor research needed)"],
            "avg_budget": "$10,000 - $40,000",
            "key_requirements": [
                "Assist user by displaying target weight [cite: 585]",
                "Read barcodes from source/destination containers [cite: 589]",
                "Import/export worklists (csv) [cite: 593, 595]"
            ]
        }
    ],
    "sample_handling_logistics": [
        {
            "solution_name": "Logistics Robot 1: Tube Handling & Weighing (URS APL07)",
            "description": "A logistics robot to fix the bottleneck of manually handling 23,000+ tubes/year[cite: 353, 372]. It automates labeling, barcoding, weighing, and pick & place operations[cite: 894, 920].",
            "example_vendors": ["(Vendor research needed)"],
            "avg_budget": "$150,000 - $300,000",
            "key_requirements": [
                "Pick & place tubes between different rack types (e.g., rack80 to Genevac racks) [cite: 924]",
                "Weigh and barcode >25,000 tubes/year [cite: 943]",
                "Weigh rack of 24 tubes in < 20 min [cite: 943]",
                "Controlled via API / worklists [cite: 928]"
            ]
        },
        {
            "solution_name": "Logistics Robot 2: Liquid Handling (URS APL08)",
            "description": "A logistics robot focused on liquid handling steps for synthesis and purification[cite: 962].",
            "example_vendors": ["(Vendor research needed)"],
            "avg_budget": "$100,000 - $250,000",
            "key_requirements": [
                "Aspirate/dispense volumes from 5µl to 30ml [cite: 988]",
                "Pool fractions from rack-to-rack [cite: 990]",
                "Redissolve dried fractions in racks [cite: 990]",
                "Controlled via API / worklists [cite: 994]"
            ]
        }
    ]
}


import os
from pydantic import BaseModel, Field
from typing import List, Optional
from agno.agent import Agent
from agno.models.lmstudio import LMStudio  # Using your working setup
from agno.tools import tool

# --- PHASE 1: THE KNOWLEDGE BASE (DATABASE) ---
# This is our mock DB of expert knowledge for the hackathon.
# It maps problems (e.g., 'sample_processing') to solutions.


# --- PHASE 2: DEFINE THE DATA STRUCTURES (Pydantic) ---
# This is the "strukturierter URS-Output" (structured output)
# the hackathon PDF mentions[cite: 14].

# --- PHASE 2: DEFINE THE DATA STRUCTURES (Pydantic) ---
# This is the "strukturierter URS-Output"
# We are simplifying it to focus on "bottlenecks" 

class LabRequirements(BaseModel):
    """The structured data form for a user's lab automation needs."""
    problem_domain: str = Field(..., description="The main lab *bottleneck* to be automated, e.g., 'weighing', 'sample_handling_logistics', 'data_analysis'.")
    samples_per_day: int = Field(..., description="The total number of samples the user needs to process per day.")
    current_process: str = Field(..., description="A brief description of the current manual process, e.g., 'manually moving tubes between racks'.")
    budget: Optional[str] = Field(None, description="The user's estimated budget, e.g., 'under 100k'.")

# --- PHASE 3: DEFINE THE AGENT'S "TOOLS" ---

@tool
def get_lab_requirements(
    problem_domain: str,
    samples_per_day: int,
    current_process: str,
    budget: Optional[str] = None
) -> LabRequirements:
    """
    Call this tool to store the user's structured lab requirements
    after you have collected all the necessary information.
    """
    print("--- [TOOL CALLED: get_lab_requirements] ---")
    reqs = LabRequirements(
        problem_domain=problem_domain,
        samples_per_day=samples_per_day,
        current_process=current_process,
        budget=budget
    )
    print(f"--- [DATA CAPTURED]: {reqs.model_dump_json(indent=2)} ---")
    
    # This tool doesn't just store, it *triggers* the solution search
    return find_automation_solution(reqs)


def find_automation_solution(requirements: LabRequirements) -> str:
    """
    Internal function (not a tool) that searches the Knowledge Base.
    This is the "Lösungsgenerator" (solution generator).
    """
    print("--- [Finding Automation Solution] ---")
    domain = requirements.problem_domain.lower().strip().replace(" ", "_")
    throughput = requirements.samples_per_day

    if domain not in SOLUTION_KNOWLEDGE_BASE:
        return f"I have understood your need for '{domain}', but I do not have a pre-built solution for that in my database."

    # Find solutions that match the domain
    possible_solutions = SOLUTION_KNOWLEDGE_BASE[domain]

    # --- Build the Summary Report ---
    summary = "--- 🤖 AI Consultant: Solution Proposal --- \n\n"
    summary += f"Based on your bottleneck with **{domain}** (processing **{throughput} samples/day** using a '{requirements.current_process}' process), I have identified the following automation solutions from my URS knowledge base:\n\n"

    for sol in possible_solutions:
        summary += f"### ✅ Recommended Solution: {sol['solution_name']}\n"
        summary += f"**What it does:** {sol['description']}\n"
        summary += f"**Estimated Budget:** {sol['avg_budget']}\n"
        
        # Add the Key Requirements from the URS
        summary += "**Key Requirements (from URS):**\n"
        for req in sol['key_requirements']:
            summary += f"* {req}\n"
        summary += "---\n"

    summary += "\nThis proposal is a starting point. We can now dive deeper into specific products."
    return summary

# --- PHASE 4: CREATE THE AGENT ---

def create_lab_agent():
    
    # These instructions are CRITICAL for the hackathon.
    agent_instructions = [
        "You are an 'AI Lab Consultant' for the 'Lab of the Future'[cite: 7].",
        "Your goal is to understand a lab manager's needs, just like an experienced consultant[cite: 10].",
        "Your PRIMARY TASK is to fill out the `LabRequirements` form by asking the user questions.",
        "Start by asking them what their main automation challenge is.",
        "You MUST find out: 1. `problem_domain`, 2. `samples_per_day`, 3. `current_process`.",
        "Be conversational! If they say 'We need to automate 500 samples', ask 'Great, what kind of samples are they? And what is the current manual process?'",
        "Once you have all the required information (problem_domain, samples_per_day, current_process), you MUST call the `get_lab_requirements` tool with the data you collected.",
        "Do not call the tool before you have all three required pieces of information.",
        "After the tool is called, present the final summary it gives you."
    ]
    
    # Use the working LMStudio setup
    MY_LMSTUDIO_MODEL_ID = "llama3:8" 

    lab_agent = Agent(
        model=LMStudio(id=MY_LMSTUDIO_MODEL_ID), 
        tools=[get_lab_requirements],
        instructions=agent_instructions,
        markdown=True,
    )
    return lab_agent

# --- PHASE 5: RUN THE PROTOTYPE (Testable Chatbot) ---

def main():
    agent = create_lab_agent()
    if agent is None:
        return
        
    print("--- 🤖 AI Lab Consultant Prototype ---")
    print("--- (Using LMStudio Model: llama3:8) ---")
    print("Type 'quit' to exit.\n")
    
    try:
        # Start the conversation
        agent.print_response("Hi, I'm your AI Lab Consultant. What automation problem can I help you solve today?")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                print("Agent: Goodbye!")
                break
            
            # This runs the agent's "brain"
            agent.print_response(user_input)
            
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
