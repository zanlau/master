import pandas as pd

if __name__ == '__main__':
    app.run_server(debug=True, port=8051) # or whatever you choose

df = pd.read_csv("Feuerwehr CH.csv")

df