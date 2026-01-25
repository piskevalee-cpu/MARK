
# =============================================================================
# Performance Panel (System Stats Only)
# =============================================================================

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from .components import COLORS

class PerformancePanel:
    """Panel showing real-time system performance metrics (Top Bar)."""
    
    @staticmethod
    def render(
        cpu_usage: float,
        ram_usage: float,
    ) -> Panel:
        """Render the system performance panel."""
        
        # Colors: < 60% good, < 80% ok, > 80% warn
        cpu_color = COLORS["success"] if cpu_usage < 60 else (COLORS["warning"] if cpu_usage < 80 else COLORS["error"])
        ram_color = COLORS["success"] if ram_usage < 60 else (COLORS["warning"] if ram_usage < 80 else COLORS["error"])

        # Grid construction
        main_table = Table.grid(expand=True, padding=(0, 4))
        
        # Add columns for balanced layout
        main_table.add_column(justify="center", ratio=1)
        main_table.add_column(justify="center", ratio=1)
        main_table.add_column(justify="center", ratio=1)
        main_table.add_column(justify="center", ratio=1)
        
        # Data
        main_table.add_row(
            Text(f"CPU: {cpu_usage:.1f}%", style=cpu_color),
            Text(f"RAM: {ram_usage:.1f}%", style=ram_color),
            Text("GPU: N/A", style=COLORS["muted"]),
            Text("TEMP: N/A", style=COLORS["muted"]),
        )
        
        return Panel(
            main_table,
            title="SYSTEM MONITOR",
            title_align="center",
            border_style=COLORS["border"],
            padding=(0, 1),
        )
