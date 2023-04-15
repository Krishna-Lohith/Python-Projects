from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
import logging

logging.basicConfig(filename = "webscrapper.log",filemode="w",level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

application = Flask(__name__)
app = application

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        string = request.form["content"].replace(" ","")
        flip_link = "https://www.flipkart.com/search?q=" + string
        uclient = uReq(flip_link)
        flip_html = uclient.read()
        uclient.close()
        try:
            flip_bs = bs(flip_html, "html.parser")
            flip_item = flip_bs.findAll("div", {"class": "_1AtVbE col-12-12"})
            del flip_item[0:3]
            box = flip_item[0]
        except Exception as e:
            logging.error("Got an error", e)
            return render_template("error.html")
        
        try:
            productlink = "https://www.flipkart.com" + box.div.div.div.a["href"]
            productreq = requests.get(productlink)
            href_html = bs(productreq.text, "html.parser")
            comments = href_html.findAll("div", {"class": "_16PBlm"})
        except Exception as e:
            logging.error("Got an error", e)
            return render_template("error.html")
        

        name = string + ".csv"
        file = open(name, "w")
        header = "product,user name,rating,comment header,comment\n"
        file.write(header)

        reviews = []
        for i in comments:
            if i.div and i.div.div and i.div.div.findAll('div', {'class': ""}):
                try:
                    comment = i.div.div.findAll('div', {'class': ""})[0].div.text
                except Exception as e:
                    comment = "No comments"
                    logging.error("Got an error", e)
                try:
                    commenter = i.div.div.findAll("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                except Exception as e:
                    commenter = "No user"
                    logging.error("Got an error", e)
                try:
                    header = i.div.div.div.findAll("p",{"class":"_2-N8zT"})[0].text
                except Exception as e:
                    header = "No header"
                    logging.error("Got an error", e)
                try:
                    rating =  i.div.div.div.div.text
                except Exception as e:
                    rating = "No rating"
                    logging.error("Got an error", e)
                d = {"product":string, "user name":commenter,"rating":rating,"comment header":header, "comment":comment}
                reviews.append(d)
        df = pd.DataFrame(reviews)
        logging.info("Successfully got the reviews")
        return render_template("results.html", result = df)
    return render_template("index.html")

if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1", port=5000)
