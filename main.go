package main

import (
	"encoding/json"
	"github.com/PuerkitoBio/goquery"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// BaseURL is base url of the site.
const BaseURL = "https://www.eatsmart.jp/"

// URLs is crawled urls.
var URLs = []string{
	"https://www.eatsmart.jp/do/caloriecheck/list/param/category/05/prevCondition/05%25E3%2581%2586%25E3%2581%25BE%25E3%2581%2584%25E6%25A3%2592/paging/YES",
	"https://www.eatsmart.jp/do/caloriecheck/list/param/category/05/prevCondition/05%25E3%2581%2586%25E3%2581%25BE%25E3%2581%2584%25E6%25A3%2592/offset/10/paging/YES",
}

type (
	// Umaibou is Umaibou  object.
	Umaibou struct {
		Name    string  `json:"name"`
		Energy  float64 `json:"energy"`
		Protein float64 `json:"protein"`
		Fat     float64 `json:"fat"`
		Carbon  float64 `json:"carbon"`
		Natrium float64 `json:"natrium"`
	}
)

func getInfo(url string, u *Umaibou) (err error) {
	doc, err := goquery.NewDocument(url)
	nPat, err := regexp.Compile(`([1-9]\d*|0)(\.\d+)?`)
	if err != nil {
		return
	}
	doc.Find(".bargraph").Each(func(i int, s *goquery.Selection) {
		s.Find(".item").Each(func(i int, s *goquery.Selection) {
			title, isExist := s.Attr("title")
			if isExist {
				r := strings.Split(title, "/")
				n := nPat.FindString(r[1])
				f, err := strconv.ParseFloat(n, 64)
				if err != nil {
					return
				}
				switch r[0] {
				case "エネルギー(kcal)":
					u.Energy = f
				case "たんぱく質(g)":
					u.Protein = f
				case "脂質(g)":
					u.Fat = f
				case "炭水化物(g)":
					u.Carbon = f
				case "ナトリウム(mg)":
					u.Natrium = f
				}
			}
		})
	})
	return
}

func dump(fname string, us []Umaibou) (err error) {
	b, err := json.MarshalIndent(us, "", "\t")
	if err != nil {
		return
	}

	if err = ioutil.WriteFile(fname, b, os.ModePerm); err != nil {
		if err = os.MkdirAll(filepath.Dir(fname), os.ModePerm); err != nil {
			return
		}
		if err = ioutil.WriteFile(fname, b, os.ModePerm); err != nil {
			return
		}
	}

	return
}

func main() {

	var umaibous []Umaibou
	for _, v := range URLs {
		doc, err := goquery.NewDocument(v)
		if err != nil {
			panic(err)
		}
		doc.Find(".result").Find("tr").Each(func(i int, s *goquery.Selection) {
			s.Find(".bOff").Each(func(i int, s *goquery.Selection) {
				if i == 0 {
					s.Find("a").Each(func(i int, s *goquery.Selection) {
						if i == 1 {
							href, isExist := s.Attr("href")
							if isExist {
								u := Umaibou{Name: strings.Fields(s.Text())[2]}
								err := getInfo(BaseURL+href, &u)
								if err != nil {
									panic(err)
								}
								umaibous = append(umaibous, u)
							}
						}
					})
					return
				}
			})
		})
	}

	if err := dump("data/umaibou.json", umaibous); err != nil {
		panic(err)
	}

}
