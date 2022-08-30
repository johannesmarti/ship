def print_consumers(allocation, province):
    world =  allocation.world()
    print(world.province_name(province), "(consumption)")
    w = allocation.wages(province)
    print("wages:", w)
    u = allocation.utility(province)
    print("utility:", utility_per_pop)
    price_of_utility = w / u
    print("price of utility:", price_of_utility)

def print_consumers(group):
    print(location_name[group], "(consumption)")
    w = wages(group)
    print("wages:", w)
    utility_per_pop = consumer.utility(consumptions[group])
    print("utility:", utility_per_pop)
    price_of_utility = w/ utility_per_pop
    print("price of utility:", price_of_utility)
    local_prices = prices[slice_of_market(group)]
    # lambda can be interpreted as the price of 1 utility
    spending = local_prices @ consumptions[group]
#    print("spending", spending)
#    print("lambda", np.sqrt(lambda_squared))
    print("local prices", local_prices)
    print("consumption", consumptions[group])
    print("utility_per_good", np.sqrt(utility_coefficients * consumptions[group]))
