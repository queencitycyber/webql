class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path
        # TODO: Implement actual config loading
        self.settings = {"default_output_dir": "webql_output"}

    def __str__(self):
        return f"Config(config_path={self.config_path})"
