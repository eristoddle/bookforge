# Direction: BookForge as a remote API for Veneer

*Planning note, 2026-10-16. High level only; details come later.*

- [Veneer](https://github.com/eristoddle/veneer), the desktop writing app, will have a BookForge plugin.
- BookForge runs as a **remote API**. The Veneer plugin is a thin client that calls it over the network (through Veneer's `api.net.fetch`).
- BookForge is in a simple state, close to a blank slate, with more features to add. It's expected to be the easier of the two integrations (the other is GitWrite).
- Open questions for later: how manuscript files get from Veneer to the API, how credentials are handled, and which features to add.
