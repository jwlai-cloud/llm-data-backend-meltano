# Build your own LLM-based application in 30 mins

This Meltano project helps you to build an LLM-based application fast by using a template repository that is easy to configure.

We're going to configure [LLM example repository from Meltano](https://github.com/meltano/llm-data-backend-meltano) to fit my own application.

I'll show you how to ...

- scrape a different website for context (my blog)
- use non-web resources as context (I'm using a CSV with a text document inside)
- adapt the cleaning mechanism (removing unicode characters)
- test the process

## Prereqs
Either be lazy and fork this repository, or fork the [the LLM example repository](https://github.com/meltano/llm-data-backend-meltano) repository 
and go step-by-step to really learn something!

You'll need:
- An OpenAI account and API key (for a paid account - even if it's just $5! Otherwise the API rate limit will be a problem)
- A Pinecone account and API key

Then:
1. Copy the `.env_template` file to `.env` and replace the sample values with your OpenAI and Pinecone values
2. Run `meltano install`

Try out the original project first by...

3. Running `meltano run reload_pinecone`
4. Running the demo app `meltano invoke streamlit_app:demo_ui`

This will scrape the "Meltano SDK" docs, chunk it into little pieces feed it into the OpenAI embeddings API, and store the resulting embedding inside pinecone.
Then it will open up a demo application you can use to ask questions and get answers based on this new embedding!

Once you're done playing around, you can follow along with my new application.

# Scraping a new website for context
If you want to still supply web-based context, then you need to configure the so-called "tap", that retrieves the
context data.

Head into the `meltano.yml` and change the configuration of `tap-beautifulsoup`. Here we're just exchanging
the website for my personal blog.

```yaml
plugins:
  extractors:
  - name: tap-beautifulsoup
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-beautifulsoup.git@v0.1.0
    config:
      source_name: sdk-docs
      site_url: https://datacisions.com #OLD VALUE: https://sdk.meltano.com/en/latest/
      output_folder: output
      parser: html.parser
      download_recursively: true
      find_all_kwargs:
        attrs:
          role: main
```

*Note: For details on the configuration, head over to [tap-beautifulsoup on the Hub](https://hub.meltano.com/extractors/tap-beautifulsoup).*

To test this modification out, just run `meltano invoke tap-beautifulsoup` and your new website should 
get downloaded into the `output` folder.

Then run `meltano reload_pinecone` to run the complete sequence of steps, create embeddings from the OpenAI
embeddings API and load it into pinecone.

Finally, you can run `meltano invoke streamlit_app:demo_ui` to play around with a demo application based on your embedding.

*Note: If you want to have see it working (with the example website above), ask this thing what the difference between "good data and bad data" is, to get an answer straight from my mouth.*

## Using non-web based context
I added another file with one of my articles as text, inside a CSV. It's inside [data/mental_models.csv](data/mental_models.csv). 

Now we're going to create an embedding based on just this one article to have a chat with this one document.

To do so, we need 
- a different kind of data source, 
- and adapt our cleaning mechanism a bit.

## Step 1 adding a new data source
On [https://hub.meltano.com/](https://hub.meltano.com/) we find over 600 data sources, including the right connector, called "tap-csv". We can install it by adding the following segment to the `meltano.yml` file and then running the `meltano install` command: 
```yaml
 - name: tap-csv
    pip_url: git+https://github.com/sbalnojan/tap-csv.git
    config:
      files:
      - entity: doc
        path: ./data/mental_models.csv
        keys: [id]
        delimiter: ;
      add_metadata_dict: True

  loaders:
  [...]
  - name: target-jsonl
    variant: andyh1203
    pip_url: target-jsonl
```

While we're at it, we're also adding a new target for jsonl, just to make testing things easier.

You can test out that everything works by running `meltano tap-csv target-jsonl`. 

## Step 2 adapting the data cleaning step
Since my document has a bunch of weird unicode characters in it, we want to adapt our text processing. This can be found inside the `mapper-generic` or more specifcally, inside the file `mappers/clean_text.py`: 

```python
        page_content = message_dict["record"]["page_content"]
        page_content = page_content.replace("Three Data Point Thursday", "").replace("Finish Slime","") # remove specific   phrases
        no_unicode = page_content.encode("ascii", "ignore").decode() # remove all unicode chars
        text_nl = " ".join(no_unicode.split("\n"))
        text_spaces = " ".join(text_nl.split())
        message_dict["record"]["page_content"] = text_spaces
        return message_dict

```

You can test everything out again by running  `meltano tap-csv clean-text target-jsonl`. 

Now that we're at this step, we can also test out our embeddings by dumping them into a local file:

`meltano run tap-csv clean-text add-embeddings target-jsonl`

## Step 3 reload pinecone from our CSV

To finally reload our embeddings inside pinecone and thus our application from this one document,
simply run 

`meltano run tap-csv clean-text add-embeddings target-pinecone`

Again, run

`meltano invoke streamlit_app:demo_ui`

to open up the chat dialog, and enjoy!

