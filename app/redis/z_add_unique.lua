local z_key = KEYS[1]
local nbytes = ARGV[1]
local score = ARGV[2]
local seed = ARGV[3]
math.randomseed(seed)
local generate = function()
    local strings = {}
    for i=0, nbytes do
        strings[i] = bit.tohex(math.random(255), 2)
    end
    return table.concat(strings)
end
local id = generate()
while not redis.zscore(z_key, id) do
    local id = generate()
end
redis.zadd(z_key, score, id)
return id
