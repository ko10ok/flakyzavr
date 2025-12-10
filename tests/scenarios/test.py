import vedro

class Scenario(vedro.Scenario):
    subject = 'a placeholder test scenario'
    env = 'default'

    async def when_nothing_happens(self):
        pass

    async def then_nothing_should_change(self):
        pass
