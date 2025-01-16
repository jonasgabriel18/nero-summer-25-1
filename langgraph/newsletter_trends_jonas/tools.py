# Importar a biblioteca necessária
from pytrends.request import TrendReq
from langchain_core.tools import StructuredTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from typing import List
from tqdm import tqdm
from pydantic import BaseModel, Field
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import os

load_dotenv()

# Inicializar um objeto TrendReq
pytrends = TrendReq(hl='pt-BR', tz=360)

def to_list(text):
    return text.split("\n")

def trends_per_country(country: str, head: int) -> str:
    """trends per country"""
    country = country.lower()
    daily_trending_searches = pytrends.trending_searches(pn=country)
    word_list = daily_trending_searches.head(head).values.T[0]
    return "\n".join(word_list)

async def atrends_per_country(country: str, head: int) -> str:
    """trends per country"""
    country = country.lower()
    daily_trending_searches = pytrends.trending_searches(pn=country)
    word_list = daily_trending_searches.head(head).values.T[0]
    return "\n".join(word_list)

def create_trends_tool():
    return StructuredTool.from_function(func=trends_per_country, coroutine=atrends_per_country)

def get_serper_results(queries: List[str],
                       k: int=5,
                       type_content: str='news',
                       hl: str='pt',
                       gl: str='br') -> List[dict]:
    
    """
    Get the multiple search results from Google Serper API
    
    Args:
    - queries: List of queries to be searched
    - k: Number of results to be returned
    - type_content: Type of content to be searched
    - hl: Language to be searched
    - gl: Country to be searched
    
    Returns:
    - List of results from the search
    
    """

    search = GoogleSerperAPIWrapper(gl=gl,
                                    hl=hl,
                                    k=k, 
                                    type=type_content)
    
    results = [search.results(query) for query in queries]
    return results

def get_serper_with_scrapping(queries: List[str],
                              k: int=5,
                              type_content: str='news',
                              hl: str='pt',
                              gl: str='br') -> List[dict]:
    
    """
    Get the multiple search results from Google Serper API and scrap the content
    
    Args:
    - queries: List of queries to be searched
    - k: Number of results to be returned
    - type_content: Type of content to be searched
    - hl: Language to be searched
    - gl: Country to be searched
    
    Returns:
    - List of results from the search
    """
    
    results = get_serper_results(queries, 
                                 k, 
                                 type_content, 
                                 hl, 
                                 gl)
    
    dict_results_news = {}
    for r in tqdm(results):
        q = r['searchParameters']['q']
        news = r['news']
        
        for i in range(len(news)):
            n = news[i]
            link = n['link']
            loader = WebBaseLoader(web_paths=[link])
            docs = loader.load()
            news[i]['content'] = "\n".join([x.page_content for x in docs])
        
        dict_results_news[q] = news
        
    return dict_results_news

class GetSchema(BaseModel):
    """Schema de futebol"""
    
    resultado: str = Field(description="YES caso o texto fale de FUTEBOL e NO caso contrário", examples=['YES', 
                                                                                                        'NO'])

def llm_structured_extraction_classifier(model_name_openai = "gpt-4o-2024-08-06"):

    llm_openai = ChatOpenAI(
        model=model_name_openai,
        temperature=0,
    )

    system_prompt = """
        Você é um assistente de IA muito prestativo que vai auxiliar um jornalista a classificar textos que falam especificamente sobre FUTEBOL.
        Você precisa classificar o texto como YES ou NO, dependendo se o texto fala de futebol ou não.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt), 
            ("human", "query do usuário: \n\n {query}")
        ]
    )

    llm_openai_with_tools_extraction = llm_openai.bind_tools([GetSchema])
    chain_openai_structured_extraction = prompt | llm_openai_with_tools_extraction

    return chain_openai_structured_extraction

def classify_soccer_news(news: dict, 
                         model_name_openai = "gpt-4o-2024-08-06") -> dict:
    """
    Classify the news as soccer or not soccer.
    
    Args:
        news: dict of news about each trend
        model_name_openai: name of the language model
    """

    chain_openai_structured_extraction = llm_structured_extraction_classifier(model_name_openai)

    soccer_news = {}

    for trend, content in news.items():
        soccer_news[trend] = []
        for i, new in enumerate(content):
            # title = new["title"]
            txt_content = new["content"]
            # link = new["link"]
            
            response = chain_openai_structured_extraction.invoke({"query": txt_content})
            resultado = response.tool_calls[0]["args"]["resultado"]

            if resultado == "YES":
                soccer_news[trend].append(new)
    
    filtered_soccer_news = {k: v for k, v in soccer_news.items() if v}
    
    return filtered_soccer_news