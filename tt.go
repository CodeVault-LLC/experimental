package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"regexp"
	"sort"
	"strings"
)

// TokenizeJS processes a JavaScript file URL and extracts significant tokens.
func TokenizeJS(name string) []string {
	queryParamRegex := regexp.MustCompile(`\?([^#]*)`)
	pathRegex := regexp.MustCompile(`/[a-zA-Z0-9_\-]+\.js`)

	// Regex to filter out dynamic values (e.g., timestamps, random hashes)
	dynamicFilterRegex := regexp.MustCompile(`[0-9a-fA-F]{10,}`)

	// Extract and filter tokens
	tokens := []string{}

	// Extract origin and path
	parsedURL, err := url.Parse(name)
	if err == nil {
		if parsedURL.Scheme != "" {
			tokens = append(tokens, parsedURL.Scheme)
		}
		if parsedURL.Host != "" {
			tokens = append(tokens, parsedURL.Host)
		}
		if parsedURL.Path != "" {
			pathMatches := pathRegex.FindAllString(parsedURL.Path, -1)
			tokens = append(tokens, pathMatches...)
		}
	}

	// Extract query parameters
	matches := queryParamRegex.FindAllStringSubmatch(name, -1)
	for _, match := range matches {
		if len(match) > 1 {
			params := strings.Split(match[1], "&")
			for _, param := range params {
				key := strings.SplitN(param, "=", 2)[0]
				tokens = append(tokens, key)
			}
		}
	}

	// Filter out dynamic values
	filteredTokens := []string{}
	for _, token := range tokens {
		if !dynamicFilterRegex.MatchString(token) {
			filteredTokens = append(filteredTokens, token)
		}
	}

	// Deduplicate and sort tokens for stable output
	tokenSet := make(map[string]struct{})
	for _, token := range filteredTokens {
		tokenSet[token] = struct{}{}
	}

	sortedTokens := make([]string, 0, len(tokenSet))
	for token := range tokenSet {
		sortedTokens = append(sortedTokens, token)
	}
	sort.Strings(sortedTokens)

	return sortedTokens
}

// NormalizeContent processes JavaScript file content to extract a normalized structure.
func NormalizeContent(content string) string {
	// Remove comments
	commentRegex := regexp.MustCompile(`(?s)//.*?$|/\*.*?\*/`)
	normalized := commentRegex.ReplaceAllString(content, "")

	// Remove extra whitespace
	normalized = strings.TrimSpace(normalized)
	normalized = regexp.MustCompile(`\s+`).ReplaceAllString(normalized, " ")

	// Replace function names with a generic name
	functionRegex := regexp.MustCompile(`function\s+([a-zA-Z0-9_]+)\s*\(`)
	normalized = functionRegex.ReplaceAllString(normalized, "function $1(")

	variableRegex := regexp.MustCompile(`var\s+([a-zA-Z0-9_]+)\s*=`)
	normalized = variableRegex.ReplaceAllString(normalized, "var $1 =")

	stringRegex := regexp.MustCompile(`(['"])[^'"]*(['"])`)
	normalized = stringRegex.ReplaceAllString(normalized, "$1$2")

	numberRegex := regexp.MustCompile(`\b[0-9]+\b`)
	normalized = numberRegex.ReplaceAllString(normalized, "0")

	return normalized
}

// ContentBasedFingerprint generates a fingerprint from the normalized content.
func ContentBasedFingerprint(content string) string {
	normalized := NormalizeContent(content)
	hasher := sha256.New()
	hasher.Write([]byte(normalized))
	return hex.EncodeToString(hasher.Sum(nil))
}

// GenerateFingerprint computes a stable hash from the extracted tokens.
func GenerateFingerprint(tokens []string, content string) string {
	// Token-based fingerprint
	tokenHasher := sha256.New()
	for _, token := range tokens {
		tokenHasher.Write([]byte(token))
	}
	tokenFingerprint := hex.EncodeToString(tokenHasher.Sum(nil))

	contentFingerprint := ContentBasedFingerprint(content)

	// Combine both fingerprints
	hasher := sha256.New()
	hasher.Write([]byte(tokenFingerprint + contentFingerprint))
	return hex.EncodeToString(hasher.Sum(nil))
}

// Example usage
func main() {
	names := []string{
		"https://apis.google.com/_/scs/abc-static/_/js/k=gapi.gapi.en.x7CxCIZpks8.O/m=gapi_iframes,googleapis_client/rt=j/sv=1/d=1/ed=1/am=AAAg/rs=AHpOoo8czmnaLIncRgBQP7N2THncpDJ9mQ/cb=gapi.loaded_0",
		"https://apis.google.com/_/scs/abc-static/_/js/k=gapi.gapi.en.x7CxCIZpks8.O/m=gapi_iframes,googleapis_client/rt=j/sv=1/d=1/ed=1/am=AAAg/rs=AHpOoo8czmnaLIncRgBQP7N2THncpDJ9mQ/cb=gapi.loaded_0",
		"https://ogads-pa.googleapis.com/$rpc/google.internal.onegoogle.asyncdata.v1.AsyncDataService/GetAsyncData",
		"https://www.google.com/complete/search?q&cp=0&client=gws-wiz&xssi=t&gs_pcrt=2&hl=no&authuser=0&psi=LA1bZ_nLM_mz5OUP_PCDIQ.1734020399693&dpr=1&nolsbt=1",
		"https://www.gstatic.com/og/_/js/k=og.qtm.en_US.kK1dM3um3so.2019.O/rt=j/m=qabr,q_dnp,qcwid,qapid,qald,qads,q_dg/exm=qaaw,qadd,qaid,qein,qhaw,qhba,qhbr,qhch,qhga,qhid,qhin/d=1/ed=1/rs=AA2YrTvy5aateSbmVFHM0FBRaHBJsFE_CQ",
		"https://www.gstatic.com/og/_/ss/k=og.qtm.zyyRgCCaN80.L.W.O/m=qcwid,d_b_gm3,d_wi_gm3,d_lo_gm3/excm=qaaw,qadd,qaid,qein,qhaw,qhba,qhbr,qhch,qhga,qhid,qhin/d=1/ed=1/ct=zgms/rs=AA2YrTs4SLbgh5FvGZPW_Ny7TyTdXfy6xA",
	}

	for _, name := range names {
		tokens := TokenizeJS(name)
		fmt.Println("Extracted Tokens:", tokens)

		content, err := http.Get(name)
		if err != nil {
			fmt.Println("Failed to fetch content:", err)
			continue
		}

		body, err := io.ReadAll(content.Body)
		if err != nil {
			log.Fatalln(err)
		}

		// Generate fingerprint
		fingerprint := GenerateFingerprint(tokens, string(body))
		fmt.Println("Generated Fingerprint:", fingerprint)
	}
}
