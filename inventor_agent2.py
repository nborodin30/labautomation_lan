import os
from pydantic import BaseModel, Field
from typing import List, Optional
from agno.agent import Agent
from agno.models.lmstudio import LMStudio # Or any other model
from agno.tools import tool

# --- PHASE 1: DEFINE THE DATA STRUCTURES (Pydantic) ---
# This is the "strukturierter URS-Output" (structured output) 
# We are modeling it *directly* on the URS APL01 document 
# for a new Automated Weighing Station.

class WeighingStationURS(BaseModel):
    """
    A structured User Requirements Specification (URS) for an automated weighing station.
    This model captures the key requirements a consultant needs to build a spec document.
    """
    project_scope: str = Field(..., description="A brief summary of what this station needs to do. e.g., 'Automate weighing of solids and liquids for synthesis reactions'.")
    
    throughput: str = Field(..., description="The required throughput. e.g., 'Must support one campaign of 84 compounds per day'.")
    
    weighing_specs: str = Field(..., description="The required weighing range and precision. e.g., '0.2mg – 100g with 0.1mg precision'.")
    
    chemical_types: List[str] = Field(..., description="A list of chemical categories to be handled. e.g., ['Free-flowing powder', 'Flakes', 'Liquids (standard viscosity)'].")
    
    labware_containers: List[str] = Field(..., description="A list of source and destination containers. e.g., ['Standard Sigma-Aldrich bottles', '8ml reaction vials'].")
    
    identification_labeling: str = Field(..., description="Requirements for barcodes and labeling. e.g., 'Must read barcodes from source containers and print new barcodes for destination vials'.")
    
    data_handling: str = Field(..., description="How the system should get and export data. e.g., 'Import worklists from CSV/XML files and export a list of all resulting weights'.")
    
    workflow_use_cases: List[str] = Field(..., description="The types of weighing workflows needed. e.g., ['one-to-many', 'many-to-one'].")

# --- PHASE 2: DEFINE THE AGENT'S "TOOLS" ---
# This tool is the *final step* of the Requirements Engineering process.
# It takes all the gathered information and generates the formal URS output.

@tool
def generate_weighing_station_urs(
    project_scope: str,
    throughput: str,
    weighing_specs: str,
    chemical_types: List[str],
    labware_containers: List[str],
    identification_labeling: str,
    data_handling: str,
    workflow_use_cases: List[str]
) -> str:
    """
    Call this tool *only* after you have gathered all the required information
    from the user to populate the WeighingStationURS. This tool generates
    the final structured URS document.
    """
    
    # Create the structured data object
    urs_data = WeighingStationURS(
        project_scope=project_scope,
        throughput=throughput,
        weighing_specs=weighing_specs,
        chemical_types=chemical_types,
        labware_containers=labware_containers,
        identification_labeling=identification_labeling,
        data_handling=data_handling,
        workflow_use_cases=workflow_use_cases
    )
    
    print("--- [TOOL CALLED: generate_weighing_station_urs] ---")
    print(f"--- [DATA CAPTURED]: {urs_data.model_dump_json(indent=2)} ---")

    # --- Build the Final URS Report ---
    # This string *is* the "strukturierter URS-Output"
    
    report = "--- 📋 AI Consultant: Generated URS Document (APL01-Draft) --- \n\n"
    report += "Thank you. Based on our interview, I have drafted the following User Requirements Specification (URS) for the new **Automated Weighing Station**.\n\n"
    
    report += f"### 1. Project Scope\n"
    report += f"* {urs_data.project_scope}\n\n"
    
    report += f"### 2. Throughput\n"
    report += f"* {urs_data.throughput} [cite: 562]\n\n"
    
    report += f"### 3. Weighing Specifications\n"
    report += f"* **Range & Precision:** {urs_data.weighing_specs} [cite: 554]\n\n"
    
    report += f"### 4. Categories of Chemicals\n"
    report += "The system must handle: [cite: 556]\n"
    for item in urs_data.chemical_types:
        report += f"* {item}\n"
    report += "\n"
    
    report += f"### 5. Labware\n"
    report += "The system must handle: [cite: 558]\n"
    for item in urs_data.labware_containers:
        report += f"* {item}\n"
    report += "\n"
    
    report += f"### 6. Identification & Labeling\n"
    report += f"* {urs_data.identification_labeling} [cite: 560]\n\n"
    
    report += f"### 7. Input/Output Data\n"
    report += f"* {urs_data.data_handling} [cite: 566]\n\n"
    
    report += f"### 8. Workflows / Use Cases\n"
    report += "The system must support: [cite: 568]\n"
    for item in urs_data.workflow_use_cases:
        report += f"* {item}\n"
    report += "\n---\n"
    report += "This draft can now be used for the 'Solution Finding' phase."
    
    return report

# --- PHASE 3: CREATE THE AGENT ---

def create_requirements_agent():
    
    # These instructions guide the agent to *ask questions* to fill the URS
    agent_instructions = [
        "You are an 'AI Requirements Engineer' for the 'Lab of the Future'[cite: 7].",
        "Your goal is to conduct a 'Customer Interview' to 'Understand Needs' (Bedarf verstehen)[cite: 10].",
        "Your FINAL OUTPUT will be a 'strukturierter URS-Output' (structured URS output).",
        "Your task right now is to interview a lab manager to create a URS for a new **Automated Weighing Station**.",
        "You MUST ask questions to gather all the information needed for the `WeighingStationURS` model.",
        "Ask questions conversationally, one or two at a time. Do not overwhelm the user.",
        "Start by asking about the main goal (project_scope) and the number of samples (throughput).",
        "Then, ask about the technical details: weighing range, chemicals, labware, barcodes, and data formats.",
        "Refer to the 'URS APL01' document  as your mental guide for what questions to ask.",
        "Once you have ALL the information (project_scope, throughput, weighing_specs, chemical_types, labware_containers, identification_labeling, data_handling, workflow_use_cases), you MUST call the `generate_weighing_station_urs` tool.",
        "Do not call the tool until you have all 8 pieces of information."
    ]
    
    # Use your working LMStudio (or other) model
    MY_LMSTUDIO_MODEL_ID = "llama3:8" 

    req_agent = Agent(
        model=LMStudio(id=MY_LMSTUDIO_MODEL_ID), 
        tools=[generate_weighing_station_urs],
        instructions=agent_instructions,
        markdown=True,
    )
    return req_agent

# --- PHASE 4: RUN THE PROTOTYPE (Testable Chatbot) ---

def main():
    agent = create_requirements_agent()
    if agent is None:
        return
        
    print("--- 🤖 AI Requirements Engineer Prototype ---")
    print("--- (This agent will interview you to create a URS) ---")
    print("Type 'quit' to exit.\n")
    
    try:
        # Start the interview
        agent.print_response("Hi, I'm your AI Requirements Engineer. I'm here to help you draft a User Requirements Specification (URS) for a new automated weighing station.  \n\nTo start, could you briefly describe the main goal of this new station?")
        
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