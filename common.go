package discovery

import (
	"encoding/json"
	"io/ioutil"
	"log"
)

const (
	configFile = "/opt/discovery/etc/config.json"
)

type Config struct {
	Context struct {
		Password string `json:"password"`
		Username string `json:"username"`
	} `json:"context"`
	Email struct {
		Host     string `json:"host"`
		Password string `json:"password"`
		Port     int    `json:"port"`
		Username string `json:"username"`
	} `json:"email"`
	Sentry struct {
		AppID    string `json:"app_id"`
		Password string `json:"password"`
		User     string `json:"user"`
	} `json:"sentry"`
	URL struct {
		BaseURL           string `json:"base_url"`
		ContextBaseURL    string `json:"context_base_url"`
		NewsProcessingURL string `json:"news_processing_url"`
	} `json:"url"`
}

func NewConfig() *Config {
	config := Config{}

	readBytes, err := ioutil.ReadFile(configFile)
	if err != nil {
		log.Fatalf("Cannot read config file: %s %s", config, err)
	}

	err = json.Unmarshal(readBytes, &config)
	if err != nil {
		log.Fatalf("Cannot parse JSON in config file: %s %s", config, err)
	}

	return &config
}
