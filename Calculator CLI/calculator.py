# Simple CLI Calculator with Stack History (No Undo)

class SimpleCalculator:

    def __init__(self):
        self.history_stack = []   # Stack for history

    # Calculate expression
    def calculate(self, expr):
        try:
            result = eval(expr)

            record = f"{expr} = {result}"

            # Push into stack
            self.history_stack.append(record)

            return result

        except:
            return "Invalid Expression"

    # Show History
    def show_history(self):
        if not self.history_stack:
            print("\nNo history yet.\n")
            return

        print("\n--- HISTORY (Latest First) ---")

        # Stack: print from top
        for item in reversed(self.history_stack):
            print(item)


    # Main CLI Loop
    def run(self):

        while True:

            print("\n=== SIMPLE CLI CALCULATOR ===")
            print("1. Calculate")
            print("2. Show History")
            print("3. Exit")

            choice = input("Choose: ")

            if choice == "1":
                expr = input("Enter expression: ")

                result = self.calculate(expr)

                print("Result:", result)

            elif choice == "2":
                self.show_history()

            elif choice == "3":
                print("Bye Bro 👋")
                break

            else:
                print("Invalid Option")


# Run Program
app = SimpleCalculator()
app.run()