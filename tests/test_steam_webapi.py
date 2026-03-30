from rf2settings.valve import steam_webapi


def test_steam_webapi():
    response = steam_webapi.get_server_list(limit=10)
    
    # Check response is not empty and contains servers list
    assert response, "Response should not be empty"
    assert 'response' in response, "Response should contain 'response' key"
    
    servers = response['response']['servers']
    assert isinstance(servers, list), "Servers should be a list"
    assert len(servers) > 0, "Should receive at least one server"
    
    # Verify first server has expected schema
    server = servers[0]
    assert 'addr' in server, "Server should have 'addr' (address)"
    assert 'gameport' in server, "Server should have 'gameport'"
    assert 'steamid' in server, "Server should have 'steamid'"
    assert 'name' in server, "Server should have 'name'"
    assert 'appid' in server, "Server should have 'appid'"
    assert 'players' in server, "Server should have 'players'"
    assert 'max_players' in server, "Server should have 'max_players'"
    
    # Verify types
    assert isinstance(server['addr'], str), "addr should be string"
    assert isinstance(server['gameport'], int), "gameport should be int"
    assert isinstance(server['appid'], int), "appid should be int"
    assert server['appid'] == 365960, "appid should be 365960 (rFactor 2)"
