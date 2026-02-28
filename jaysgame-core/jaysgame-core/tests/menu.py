class Menu:
    # Constructor
    def __init__(self):
        self.options = {}
        self.setPrompt("Please choose an option:")
        self.setErrorText("Error! Please enter a valid option.")

    # Adds an option to this Menu. An option consists of a number,
    # name, and the actual object it corresponds to (submenu or procedure).
    # The last value in each key-value pair denotes whether the given option
    # should trigger an exit from the current Menu after it is called.
    def addOption(self, optionNumber, optionName, option, TriggersExit):
        self.options[optionNumber] = [optionName, option, TriggersExit]

    # Sets this Menu's error text
    def setErrorText(self, errorText):
        self.errorText = errorText

    # Sets this Menu's prompt
    def setPrompt(self, prompt):
        self.prompt = prompt

    # Returns the number of options in this Menu
    def size(self):
        return len(self.options)

    # Displays this Menu's error text
    def displayError(self):
        print("\n{}\n".format(self.errorText))

    # Prints the Menu in its entirety
    def display(self):
        print(self.prompt)
        for i in range(1, self.size()+1):
            print("{} - {}".format( i, self.options[i][0] ))
        print()

    # Runs this Menu
    def run(self):
        userInput = ""
        self.display()
        while True:
            userInput = input("Your selection: ")
            try:
                userInput = int(userInput)
                if userInput <= 0 or userInput > self.size():
                    self.displayError()
                else:
                    # If the menu option is a function, call it
                    if callable(self.options[userInput][1]):
                        self.options[userInput][1]()
                        # And if it's an option that triggers a return/exit, then return after it's called
                        if self.options[userInput][2]:
                            return
                        # Otherwise, redisplay the menu options
                        else:
                            self.display()
                    # But if the menu option is a submenu, run it
                    else:
                        self.options[userInput][1].run()
                        # And display the calling menu's options again upon return from the submenu
                        self.display()
            except ValueError:
                self.displayError()