# app.py
import abc
from flask import Flask, render_template, request, jsonify

# --- The Expense Class (Request) ---
class Expense:
    """A simple class to represent an expense report."""
    def __init__(self, amount, purpose="General Expense"):
        self.amount = amount
        self.purpose = purpose

    def __str__(self):
        return f"Expense for '{self.purpose}' amounting to ${self.amount:,.2f}"

# --- The Handler Interface ---
class Approver(abc.ABC):
    """The Handler interface for building the chain."""
    def __init__(self):
        self._next_approver = None

    def set_next(self, approver: 'Approver') -> 'Approver':
        self._next_approver = approver
        return approver

    @abc.abstractmethod
    def handle_expense(self, expense: Expense) -> dict:
        """
        Handles the expense and returns a result dictionary containing
        the log, final message, and final approver.
        """
        pass

# --- Concrete Handlers ---
class JuniorApprover(Approver):
    """Handles small expenses."""
    APPROVAL_LIMIT = 500
    NAME = "Junior"

    def handle_expense(self, expense: Expense) -> dict:
        if expense.amount <= self.APPROVAL_LIMIT:
            log = [f"Junior Approver: I can approve this. Approved. -> {expense}"]
            return {"log": log, "final_message": log[-1], "final_approver": self.NAME}
        elif self._next_approver:
            result = self._next_approver.handle_expense(expense)
            result["log"].insert(0, f"Junior Approver: Cannot approve. Passing up...")
            return result
        
        log = [f"No one in the chain could approve this expense: {expense}"]
        return {"log": log, "final_message": log[-1], "final_approver": None}

class ManagerApprover(Approver):
    """Handles medium expenses."""
    APPROVAL_LIMIT = 5000
    NAME = "Manager"

    def handle_expense(self, expense: Expense) -> dict:
        if expense.amount <= self.APPROVAL_LIMIT:
            log = [f"Manager: I have the authority. Approved. -> {expense}"]
            return {"log": log, "final_message": log[-1], "final_approver": self.NAME}
        elif self._next_approver:
            result = self._next_approver.handle_expense(expense)
            result["log"].insert(0, f"Manager: Above my pay grade. Passing up...")
            return result
        
        log = [f"No one in the chain could approve this expense: {expense}"]
        return {"log": log, "final_message": log[-1], "final_approver": None}

class DirectorApprover(Approver):
    """Handles large expenses."""
    APPROVAL_LIMIT = 20000
    NAME = "Director"

    def handle_expense(self, expense: Expense) -> dict:
        if expense.amount <= self.APPROVAL_LIMIT:
            log = [f"Director: This is significant, but it is approved. -> {expense}"]
            return {"log": log, "final_message": log[-1], "final_approver": self.NAME}
        
        log = [f"Director: This expense of ${expense.amount:,.2f} is too large. REJECTED."]
        return {"log": log, "final_message": log[-1], "final_approver": self.NAME}

# --- Flask Web Application ---
app = Flask(__name__)

# Build the chain of responsibility once
junior = JuniorApprover()
manager = ManagerApprover()
director = DirectorApprover()
junior.set_next(manager).set_next(director)
approval_chain_start = junior

@app.route("/")
def index():
    """Renders the main web page."""
    return render_template("index.html")

@app.route("/process_expense", methods=["POST"])
def process_expense():
    """Processes the expense amount submitted from the web page."""
    try:
        data = request.get_json()
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Please enter a positive amount."}), 400

        expense_to_process = Expense(amount)
        result = approval_chain_start.handle_expense(expense_to_process)
        # Rename 'log' to 'detailed_log' for clarity in the response
        result['detailed_log'] = result.pop('log')
        return jsonify(result)

    except (ValueError, KeyError):
        return jsonify({"error": "Invalid input. Please enter a number."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)