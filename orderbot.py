import os
import openai
import panel as pn
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# ── Helper functions ──────────────────────────────────────────────────────────

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


# ── Panel GUI ─────────────────────────────────────────────────────────────────

pn.extension()

panels = []   # collect display rows

context = [
    {
        'role': 'system',
        'content': """
You are OrderBot, an automated service to collect orders for a pizza restaurant.
You first greet the customer, then collect the order,
and then ask if it's a pickup or delivery.
You wait to collect the entire order, then summarize it and check for a final
time if the customer wants to add anything else.
If it's a delivery, you ask for an address.
Finally you collect the payment.
Make sure to clarify all options, extras and sizes to uniquely
identify the item from the menu.
You respond in a short, very conversational friendly style.

The menu includes:

Pizzas:
  pepperoni pizza   12.95 (large), 10.00 (medium), 7.00 (small)
  cheese pizza      10.95 (large),  9.25 (medium), 6.50 (small)
  eggplant pizza    11.95 (large),  9.75 (medium), 6.75 (small)

Sides:
  fries             4.50 (large), 3.50 (small)
  greek salad       7.25

Toppings:
  extra cheese      2.00
  mushrooms         1.50
  sausage           3.00
  canadian bacon    3.50
  AI sauce          1.50
  peppers           1.00

Drinks:
  coke              3.00 (large), 2.00 (medium), 1.00 (small)
  sprite            3.00 (large), 2.00 (medium), 1.00 (small)
  bottled water     5.00
"""
    }
]


def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''

    context.append({'role': 'user', 'content': f"{prompt}"})
    response = get_completion_from_messages(context)
    context.append({'role': 'assistant', 'content': f"{response}"})

    panels.append(
        pn.Row('🧑 User:',
               pn.pane.Markdown(prompt, width=600))
    )
    panels.append(
        pn.Row('🤖 OrderBot:',
               pn.pane.Markdown(response, width=600,
                                styles={'background-color': '#F6F6F6',
                                        'padding': '8px',
                                        'border-radius': '6px'}))
    )
    return pn.Column(*panels)


# ── Widgets ───────────────────────────────────────────────────────────────────

inp = pn.widgets.TextInput(value="Hi", placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Chat!", button_type="primary")

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    pn.pane.Markdown("## 🍕 Pizza OrderBot"),
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=400),
)

dashboard.servable()