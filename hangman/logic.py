from hangman.utils import get_random_word
class Hangman():
    def __init__(self):
        self.word = get_random_word().lower()
        self.incorrect=0
        self.guessed = ["_"] * len(self.word)
        self.guessed_letters = []
        self.game_over=False
        self.win=False

    def check_guess(self, guess):
        if guess and guess in self.word:
            for i in range(len(self.word)):
                if self.word[i] == guess:
                    self.guessed[i] = guess
        else:
            self.guessed_letters.append(guess)
            self.incorrect += 1

    def check_win(self):
        #win condition
        if "_" not in self.guessed :
            self.game_over=True
            self.win=True
        #lose condition
        elif self.incorrect >= 6:
            self.game_over=True

    def draw_hangman(self): 
        svg = '<svg width="200" height="200">' # Draw the gallows and rope first 
        svg += '<path d="M 50,150 L 150,150" stroke="black" stroke-width="2" fill="none"/>' # Base 
        svg += '<path d="M 50,50 L 50,150" stroke="black" stroke-width="2" fill="none"/>' # Post 
        svg += '<path d="M 50,50 L 100,50" stroke="black" stroke-width="2" fill="none"/>' # Crossbeam 
        svg += '<path d="M 100,50 L 100,60" stroke="black" stroke-width="2" fill="none"/>' # Rope 
        # Draw the hangman parts based on incorrect guesses 
        if self.incorrect >= 1: 
            svg += '<circle cx="100" cy="70" r="10" stroke="black" stroke-width="2" fill="none"/>' # Head 
        if self.incorrect >= 2: 
            svg += '<path d="M 100,80 L 100,120" stroke="black" stroke-width="2" fill="none"/>' # Body 
        if self.incorrect >= 3: 
            svg += '<path d="M 100,90 L 90,100" stroke="black" stroke-width="2" fill="none"/>' # Left Arm 
        if self.incorrect >= 4: 
            svg += '<path d="M 100,90 L 110,100" stroke="black" stroke-width="2" fill="none"/>' # Right Arm 
        if self.incorrect >= 5: 
            svg += '<path d="M 100,120 L 90,130" stroke="black" stroke-width="2" fill="none"/>' # Left Leg 
        if self.incorrect >= 6: 
            svg += '<path d="M 100,120 L 110,130" stroke="black" stroke-width="2" fill="none"/>' # Right Leg 
            svg += '</svg>' 
        return svg