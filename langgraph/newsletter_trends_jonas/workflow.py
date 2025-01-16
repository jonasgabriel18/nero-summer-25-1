from langgraph.graph import END, StateGraph
from .state import GraphState
from .nodes import *

def compile_workflow():
    """ 
    Compiles the workflow for creating a newsletter from Google Trends.
    
    Returns:
        app (StateGraph): The compiled workflow.
    """
    
    # Define the graph
    workflow = StateGraph(GraphState)
    
    # Define the nodes
    workflow.add_node("get_trends", get_trends)
    workflow.add_node("get_serper_and_scrapping", get_serper_and_scrapping)
    workflow.add_node("filter_soccer_news", filter_soccer_news)
    workflow.add_node("search_favorite_team_news", search_favorite_team_news)
    workflow.add_node("create_newsletter", create_newsletter)
    workflow.add_node("send_email", send_email)

    # Build graph
    workflow.set_entry_point('get_trends')
    workflow.add_edge("get_trends", "get_serper_and_scrapping")
    workflow.add_edge("get_serper_and_scrapping", "filter_soccer_news")
    # workflow.add_edge("filter_soccer_news", "create_newsletter")
    
    workflow.add_conditional_edges(
        "filter_soccer_news",
        has_soccer_news,
        {
            "search_favorite_team_news": "search_favorite_team_news",
            "create_newsletter": "create_newsletter"
        },
    )

    workflow.add_edge("search_favorite_team_news", "create_newsletter")
    
    workflow.add_edge("create_newsletter", "send_email")
    workflow.add_edge("send_email", END)
    # workflow.set_finish_point("create_newsletter")

    # Compile
    app = workflow.compile()
    return app