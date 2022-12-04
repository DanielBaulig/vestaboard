# Vestaboard Home Assistant Integration

## What is Vestaboard?
Vestaboard is a 6x22 characters connected split flap display for your home or office space. It comes with an app to post curated or custom messages to and an optional subscription called Vestaboard+ that allows for integration with custom services to push real-time messaging to it. But most importantly, it also comes with a free-to-use (cloud-based) API – and they have recently even released a local API.

## How do I use Vestaboard with Home Assistant?

- Request a Vestaboard local API enablement token here: [Request Local API Enablement Token](https://www.vestaboard.com/local-api)
- Install this custom integration code
- Add a Vestaboard instance on your Integrations page (requiring host and local API key)
- Use the vestaboard.post service to post to your Vestaboard

## How to post to Vestaboard using this integration

Example:
```
- service: vestaboard.post
  data:
    lines:
      - Line 1
      - With {{ "template" }}
      - Sensor: {{ states('sensor.my_sensor') }}
      - >
        {% if is_state('binary_sensor.something', 'on') %}
          Something is on
        {% else %}
          Something is off
        {% endif %}
      - Using colors: \xc1\xc2\xc3\xc4\xc5\xc6\xc7
      - Last Line
```

## What can I do with this?
I have created an automation, that among date, time and an uplifting message will display various data from my smart home, like temperature, air quality, the state of the HVAC units in my home as well as the upcoming appointment on the family calendar. But your imagination really is the limit here!

Checkout my Vestaboard in action here: [Home Assistant driving Vestaboard - YouTube](https://youtu.be/b-KxvMScREw)

## Where can I get one?
You can buy your own Vestaboard on their website. It’s a small Silicon Valley startup and the board itself is really well made and it looks stunning in any space. If you use the following referral link, you can safe $200 off the purchasing price and I will get a $200 referral bonus:

https://shop.vestaboard.com/?vbref=NWZJNJ

But feel free to skip the referral link if you don’t feel comfortable using it.
