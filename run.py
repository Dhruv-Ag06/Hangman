from hangman import create_app,scheduler
import atexit
app = create_app()
if __name__ == "__main__":
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)