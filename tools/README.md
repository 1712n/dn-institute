# Welcome to Repo Tools 🛠️

Hey there! 👋 Welcome to our repository's toolkit. We've got some nifty scripts that help keep things running smoothly. Whether you're here to calculate payouts, check article quality, or keep tabs on market health, we've got you covered! 🎉

## Payout Calculation 💰

Need to calculate a payout? We've got just the thing for you! Just type `/payout` along with some parameters, and voilà! Your payout will be ready in no time. 💸

- **Parameters:**
  - `--rate` (`-r`): The rate at which you're getting paid.
  - `--multiplier` (`-x`): Any multiplier you need to apply.

For example:
/payout -r 1 -x 2


## Quality Check ✨

Quality is key, right? Our `/articlecheck` script ensures that your articles are top-notch. Just provide your API keys and a link to your GitHub pull request, and let the magic happen. This script works seamlessly within GitHub Actions environment, leveraging the power of AI to ensure your content is up to par. 📝✅

## Market Health Reporter 📊

Stay ahead of the game with our market health reporter! Want to analyze market trends? Just use the `analyze:` command followed by the template: `analyze: pair, market, start_of_the_period, end_of_the_period`. 

For example:
analyze: bnb-btc, binance, 2024-02-02, 2024-02-07


That's it! Easy, right? Feel free to explore and make the most out of our handy tools. Happy coding! 🚀
