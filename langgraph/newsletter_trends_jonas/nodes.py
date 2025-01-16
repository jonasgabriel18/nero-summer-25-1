from IPython.display import Markdown
from .state import GraphState
from .tools import *
from .chains import *

from IPython.display import Markdown, display

def get_trends(state: GraphState) -> dict:
    """
    Get trends from Google Trends

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): 
    """
    print("---GET TRENDS---")
    print()
    country = state["country"]
    head = state["head"]
    subjects = state["subjects"] # New attribute
    
    if subjects:
        print("--> Assuntos adicionais: ", subjects) # New print
 
    # Get trends
    trends = create_trends_tool()
    trends_text = trends.invoke({"country": country, 
                                 "head": head})
    trends_list = to_list(trends_text)
    
    print("Trend List: ", trends_list)
    print()
    
    return {"country": country, 
            "head": head, 
            "trends": trends_list}

def get_serper_and_scrapping(state: GraphState) -> dict:
    """
    Get news from SerpAPI and scrap the content

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): 
    """
    print("---GET SERPER AND SCRAPPING---")
    print()
    trends = state["trends"]
    k = state["k"]
    subjects = state["subjects"] # New attribute
    
    # Get news
    news = get_serper_with_scrapping(queries=trends + subjects, k=k)
    keys_from_serper = news.keys()
    
    # Print some titles
    for trend in keys_from_serper:
        print(f"---{trend}---")
        for i in range(min(3, len(news[trend]))):
            print(news[trend][i]["title"])
        print()
    
    return {"news": news}

def filter_soccer_news(state: GraphState) -> dict:
    """
    Filter soccer news from the news

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): 
    """
    print("---FILTER SOCCER NEWS---")
    print()
    
    news = state["news"] # Get the news from GraphState that the previous node returned
    soccer_news = {}
    
    # Filter soccer news with tool
    soccer_news = classify_soccer_news(news)
    
    # Print some titles
    for trend, content in soccer_news.items():
        print(f"---{trend}---")
        for i in range(min(3, len(content))):
            print(content[i]["title"])
        print()
    
    return {"soccer_news": soccer_news}

def create_newsletter(state: GraphState) -> dict:
    """
    Create a newsletter from the news

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): 
    """

    print("---CREATE NEWSLETTER---")
    print()
    news = state["soccer_news"]
    
    # Create newsletter
    newsletter = write_newsletter(news=news, 
                                  provider="openai",
                                  model_name="gpt-4o-mini",
                                  temperature=0.2)
    print("Aqui está a newsletter: ", newsletter)
    display(Markdown(newsletter))
    return {"newsletter": newsletter}

def search_favorite_team_news(state: GraphState) -> dict:
    """
    Search for the favorite team news

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): 
    """
    print("---SEARCH FAVORITE TEAM NEWS---")
    print()
    # news = state["news"]
    favorite_team = state["favorite_team"]
    k = state["k"]
    
    favorite_team_news = get_serper_with_scrapping(queries=[favorite_team], k=k)
    keys_from_serper = favorite_team_news.keys()
    
    # Print some titles
    for trend in keys_from_serper:
        print(f"---{trend}---")
        for i in range(min(3, len(favorite_team_news[trend]))):
            print(favorite_team_news[trend][i]["title"])
        print()
    
    return {"soccer_news": favorite_team_news}

def has_soccer_news(state: GraphState) -> str:
    """
    Check if there are soccer news

    Args:
        state (dict): The current graph state

    Returns:
        node (str): 
    """
    soccer_news = state["soccer_news"]

    return "create_newsletter" if soccer_news else "search_favorite_team_news"

from email.message import EmailMessage
import ssl
import smtplib
from emails import EMAIL_SENDER, EMAIL_RECEIVERS

def send_email(state: GraphState):
    newsletter = state['newsletter']
    email_password = os.getenv("EMAIL_PASSWORD")

    subject = "Summer Nero 25 - Soccer Newsletter - Jonas"

    email_receiver = ", ".join(EMAIL_RECEIVERS)

    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(newsletter)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smpt:
        smpt.login(EMAIL_SENDER, email_password)
        smpt.sendmail(EMAIL_SENDER, email_receiver, em.as_string())