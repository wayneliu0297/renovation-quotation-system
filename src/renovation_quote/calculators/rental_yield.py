"""RentalYieldCalculator: buy-to-rent return metrics for a renovated unit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RentalYieldCalculator:
    """Estimate the return on a renovation-for-rent investment.

    All monetary inputs are in TWD. Rates are fractions (0.95 = 95%).

    Attributes:
        monthly_rent: Expected gross monthly rent.
        renovation_cost: Total renovation spend (e.g. Quotation.grand_total).
        property_value: Acquisition / capital value of the unit (0 if the
            owner already holds it and only renovation is being financed).
        occupancy_rate: Expected occupied fraction of the year.
        management_rate: Property-management cost as a fraction of gross rent.
    """

    monthly_rent: float
    renovation_cost: float
    property_value: float = 0.0
    occupancy_rate: float = 0.95
    management_rate: float = 0.10

    # -- income ------------------------------------------------------------
    @property
    def effective_monthly_rent(self) -> float:
        return self.monthly_rent * self.occupancy_rate

    @property
    def annual_gross_income(self) -> float:
        return self.effective_monthly_rent * 12

    @property
    def monthly_management_cost(self) -> float:
        return self.effective_monthly_rent * self.management_rate

    @property
    def monthly_net_profit(self) -> float:
        return self.effective_monthly_rent - self.monthly_management_cost

    @property
    def annual_net_income(self) -> float:
        return self.monthly_net_profit * 12

    # -- investment base ---------------------------------------------------
    @property
    def total_investment(self) -> float:
        return self.property_value + self.renovation_cost

    # -- yields ------------------------------------------------------------
    @property
    def gross_yield(self) -> float:
        """Annual gross income / total investment."""
        if self.total_investment <= 0:
            return 0.0
        return self.annual_gross_income / self.total_investment

    @property
    def net_yield(self) -> float:
        """Annual net income / total investment."""
        if self.total_investment <= 0:
            return 0.0
        return self.annual_net_income / self.total_investment

    @property
    def payback_months(self) -> float:
        """Months of net profit needed to recover the renovation cost."""
        if self.monthly_net_profit <= 0:
            return float("inf")
        return self.renovation_cost / self.monthly_net_profit

    def as_dict(self) -> dict:
        return {
            "monthly_rent": self.monthly_rent,
            "effective_monthly_rent": self.effective_monthly_rent,
            "renovation_cost": self.renovation_cost,
            "property_value": self.property_value,
            "total_investment": self.total_investment,
            "monthly_net_profit": self.monthly_net_profit,
            "annual_net_income": self.annual_net_income,
            "gross_yield": self.gross_yield,
            "net_yield": self.net_yield,
            "payback_months": self.payback_months,
        }
