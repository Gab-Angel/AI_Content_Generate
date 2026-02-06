from langchain_core.prompts import PromptTemplate
from src.graph.states import ResearchResult, FinalReport
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.prompt_search import system_prompt_search, human_prompt_search
from src.prompts.prompt_writer import system_prompt_writer, human_prompt_writer
from dotenv import load_dotenv
import os

load_dotenv()


llm_groq = ChatGroq(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

search_prompt = PromptTemplate.from_template(human_prompt_search)
writer_prompt = PromptTemplate.from_template(human_prompt_writer)

def search_agent(state, llm_model):
    topic = state['topic']
    idea = state['idea']

    prompt_search = search_prompt.format(topic=topic, idea=idea)

    messages = [
        SystemMessage(content=system_prompt_search),
        HumanMessage(content=prompt_search),
    ]

    structured_llm = llm_model.with_structured_output(ResearchResult)

    response = structured_llm.invoke(messages)

    return {"result_research": response}

def writer_agent(state, llm_model):
    
    type_post = state['type_post']
    tone = state['tone']
    qtd_slides = state['slides']
    research = state['result_research']
    

    prompt_writer = search_prompt.format(
        type_post=type_post,
        tone = tone,
        slides = qtd_slides,
        research = research
    )

    messages = [
        SystemMessage(content=system_prompt_writer),
        HumanMessage(content=prompt_writer),
    ]

    structured_llm = llm_model.with_structured_output(FinalReport)

    response = structured_llm.invoke(messages)

    
    return response 















if __name__ == '__main__':

    from src.graph.tools import Tools

    entrada = {
        'topic': "Inteligencia Artificial",
        'idea': "Uma pesquisa sobre como ela está afetando os negócios"
        }
    
    result = search_agent(state=entrada,llm_model=Tools.llm_with_tools )
    print(result)


# Parei no output estruturado
# Preciso criar o graph para a tool funcionar
# Preciso criar o agent_writer