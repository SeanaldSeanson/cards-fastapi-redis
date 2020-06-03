Redis

`game`: sorted set
Stores game ID values, formatted as random strings starting with `game:`. Each ID is the key to a Redis hash containing the respective game's information. Score is equal to the time of the game's creation.

`game:{game_id}`
Keys:
* `game_id`
* `state`: The current game state.
* `name`: The game name.
* `desc`: Game description created by the host.
* `host`: The player who created the game.
* `public`: (True/False) Whether the game is to be publicly listed.
* `decks`: key to a redis set of deck ID values
* `hand_size`: The number of cards each player should have in their hand.
* `prompt`: The current prompt, represented as a call ID, which should start with `call:` and be a key to a hash containing the information for a call card.
* `selection`: The response ID of the current
* `czar`: The player ID of the current czar.
* `passwd_hash`: 

`game_players:{game_id}`: set
Stores player ID values of players joined to game


`player`: Set
Stores player ID values, formatted as random strings starting with `player:`. Each ID is the key to a hash.

`player:{player_id}`: hash
Keys:
* `player_id`
* `secret`: a secret url-safe base64 string used for authentication
* `game_id`: the player's associated game
* `name`: the player's displaye name


`decks`: sorted set
Stores deck info JSON strings, sorted by time imported.

`calls:{deck_id}`: set
Stores call JSON strings

`responses:{deck_id}`: set
Stores call JSON strings
