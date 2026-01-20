"""
Main Flet application entry point for SOC Case Builder.
Initializes the UI, manages routing, and coordinates with backend services.
"""

import flet as ft
import atexit
from src.ui_flet.state import AppState
from src.ui_flet.theme import apply_dark_theme, PRIMARY_BG, PRIMARY_TEXT
from src.ui_flet.pages.case_builder_page import CaseBuilderPage
from src.ui_flet.pages.settings_page import SettingsPage
from src.ui_flet.pages.getting_started import GettingStartedPage
from src.ui_flet.utils.server_manager import start_server, stop_server


def main(page: ft.Page):
    """
    Main Flet application entry point.
    """
    # ==================== Page Configuration ====================
    
    page.title = "SOC Case Builder"
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Apply dark theme
    apply_dark_theme(page)
    
    # ==================== Initialize App State ====================
    
    app_state = AppState()

    # ==================== Initialize Server ====================

    def on_case_received(case_data):
        """Handle case received from /receive endpoint."""
        try:
            # Import case into state
            case_id = app_state.import_case_from_dict(case_data)
            app_state.select_case(case_id)
            # Callback to refresh UI - would navigate to case builder
            show_case_builder()
        except Exception as e:
            print(f"Error importing case: {e}")

    # Start Flask server
    start_server(on_case_received=on_case_received)
    
    # Register cleanup on exit
    atexit.register(stop_server)
    
    # ==================== Routing and Navigation ====================
    
    def show_case_builder():
        """Display case builder page."""
        page.clean()
        
        # Create app bar with menu
        app_bar = ft.AppBar(
            title=ft.Text("SOC Case Builder"),
            center_title=False,
            bgcolor=PRIMARY_BG,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda e: show_settings(),
                    tooltip="Settings",
                ),
                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    on_click=lambda e: show_search(),
                    tooltip="Search Cases",
                ),
                ft.IconButton(
                    icon=ft.Icons.QUERY_BUILDER,
                    on_click=lambda e: show_query_builder(),
                    tooltip="Query Builder",
                ),
                ft.IconButton(
                    icon=ft.Icons.INFO,
                    on_click=lambda e: show_stats(),
                    tooltip="Stats",
                ),
            ],
        )
        
        # Create case builder page
        case_builder = CaseBuilderPage(
            state=app_state,
            on_search_cases=lambda *args, **kwargs: show_search(),
            on_query_finder=show_query_finder,
        )
        
        page.appbar = app_bar
        page.add(case_builder)
    
    def show_settings():
        """Display settings page."""
        def on_settings_save():
            show_case_builder()
        
        def on_settings_close():
            show_case_builder()
        
        settings_page = SettingsPage(
            state=app_state,
            on_save=on_settings_save,
        )
        
        page.clean()
        page.add(settings_page)
    
    def show_search():
        """Display search cases page."""
        from src.ui_flet.pages.search_cases import SearchCasesPage
        
        def on_case_loaded(case_id):
            """Navigate to case builder after loading case."""
            show_case_builder()
        
        search_page = SearchCasesPage(
            state=app_state,
            on_load_case=on_case_loaded,
            on_close=show_case_builder,
        )
        
        page.clean()
        page.add(search_page)
    
    def show_query_builder():
        """Display query builder page."""
        from src.ui_flet.pages.query_builder import QueryBuilderPage
        
        builder_page = QueryBuilderPage(
            on_close=show_case_builder,
        )
        
        page.clean()
        page.add(builder_page)
    
    def show_query_finder():
        """Display query finder page."""
        from src.ui_flet.pages.query_finder import QueryFinderPage
        
        finder_page = QueryFinderPage(
            state=app_state,
            on_close=show_case_builder,
        )
        
        page.clean()
        page.add(finder_page)
    
    def show_stats():
        """Display stats page."""
        from src.ui_flet.pages.stats_page import StatsPage
        
        stats_page = StatsPage(
            on_close=show_case_builder,
        )
        
        page.clean()
        page.add(stats_page)
    
    def show_getting_started():
        """Display getting started page."""
        welcome = GettingStartedPage(
            on_close=show_case_builder,
        )
        
        page.clean()
        page.add(welcome)
    
    # ==================== Initialization ====================
    
    # Check if first time user
    if app_state.get_setting("first_time", True):
        show_getting_started()
    else:
        show_case_builder()


def app():
    """Entry point for running the Flet application."""
    ft.app(target=main, name="soc_case_builder")


if __name__ == "__main__":
    app()
