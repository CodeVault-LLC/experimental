package main

import (
	"fmt"
	"log"
	"regexp"
)

// FingerprintedContent defines a script pattern with its regex, name, and fingerprint
type FingerprintedContent struct {
	Regex       *regexp.Regexp
	Name        string
	Fingerprint string
}

// FingerprintedContents contains the pre-defined list of known patterns
var FingerprintedContents = []FingerprintedContent{
	{
		Name:        "Google Ads",
		Regex:       regexp.MustCompile(`googleads\.g\.doubleclick\.net/pagead/ads\?client=.*?(&|$)`),
		Fingerprint: "a4837e40726b33f6a638d293cdfb269743bed640e97c14c725593a8c0f31ad6c",
	},
	{
		Name:        "Google Analytics",
		Regex:       regexp.MustCompile(`www\.google-analytics\.com/(analytics|ga)\.js`),
		Fingerprint: "9ee414b09c47519632cfe12728ab767bc07739f21680718e75d0edca1131f827",
	},
	{
		Name:        "Google Tag Manager",
		Regex:       regexp.MustCompile(`www\.googletagmanager\.com/(gtm|gtag)/js\?id=.*?(&|$)`),
		Fingerprint: "6fafc56f9855a5f2c7bc3c722ff122f7d8079719e48e83b7b59b7c0ccc844f95",
	},
}

// TokenizeJS processes a URL and extracts tokens based on known fingerprints
func TokenizeJS(name string) []string {
	var tokens []string
	for _, content := range FingerprintedContents {
		if content.Regex.MatchString(name) {
			match := content.Regex.FindStringSubmatch(name)
			tokens = append(tokens, fmt.Sprintf("%s (Fingerprint: %s)", content.Name, content.Fingerprint))
			if len(match) > 1 {
				log.Printf("Matched Group: %v", match[1:])
			}
		}
	}
	return tokens
}

// UpdateFingerprints allows dynamic updates to the fingerprints
func UpdateFingerprints(newContent FingerprintedContent) {
	for i, content := range FingerprintedContents {
		if content.Name == newContent.Name {
			FingerprintedContents[i] = newContent
			log.Printf("Updated fingerprint for %s", content.Name)
			return
		}
	}
	FingerprintedContents = append(FingerprintedContents, newContent)
	log.Printf("Added new fingerprint for %s", newContent.Name)
}

// Example usage
func main() {
	urls := []string{
		"https://googleads.g.doubleclick.net/pagead/ads?client=ca-pub-123456789&output=html",
		"https://www.google-analytics.com/analytics.js",
		"https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX",
		"https://www.googletagmanager.com/gtag/js?id=G-YYYYYYYY&l=dataLayer",
	}

	for _, url := range urls {
		tokens := TokenizeJS(url)
		fmt.Printf("URL: %s\nExtracted Tokens: %v\n", url, tokens)
	}
}
