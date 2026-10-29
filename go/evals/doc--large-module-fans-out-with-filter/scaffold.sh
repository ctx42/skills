#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/mod

go 1.22
EOF_0
mkdir -p api
cat > api/api.go <<'EOF_1'
// Package api routes request paths to handler names.
package api

import "strings"

// Router maps path prefixes to handler names.
type Router struct {
	routes map[string]string
}

// NewRouter returns an empty Router.
func NewRouter() *Router {
	return &Router{routes: map[string]string{}}
}

func (rtr *Router) Handle(prefix, name string) {
	rtr.routes[prefix] = name
}

// match finds the handler
func (rtr *Router) Match(path string) string {
	for prefix, name := range rtr.routes {
		if strings.HasPrefix(path, prefix) {
			return name
		}
	}
	return ""
}
EOF_1
mkdir -p api
cat > api/ids.go <<'EOF_2'
package api

// handlerIDs maps a numeric route id to its handler name.
var handlerIDs = map[int]string{
	100: "h100",
	101: "h101",
	102: "h102",
	103: "h103",
	104: "h104",
	105: "h105",
	106: "h106",
	107: "h107",
	108: "h108",
	109: "h109",
	110: "h110",
	111: "h111",
	112: "h112",
	113: "h113",
	114: "h114",
	115: "h115",
	116: "h116",
	117: "h117",
	118: "h118",
	119: "h119",
	120: "h120",
	121: "h121",
	122: "h122",
	123: "h123",
	124: "h124",
	125: "h125",
	126: "h126",
	127: "h127",
	128: "h128",
	129: "h129",
	130: "h130",
	131: "h131",
	132: "h132",
	133: "h133",
	134: "h134",
	135: "h135",
	136: "h136",
	137: "h137",
	138: "h138",
	139: "h139",
	140: "h140",
	141: "h141",
	142: "h142",
	143: "h143",
	144: "h144",
	145: "h145",
	146: "h146",
	147: "h147",
	148: "h148",
	149: "h149",
	150: "h150",
	151: "h151",
	152: "h152",
	153: "h153",
	154: "h154",
	155: "h155",
	156: "h156",
	157: "h157",
	158: "h158",
	159: "h159",
	160: "h160",
	161: "h161",
	162: "h162",
	163: "h163",
	164: "h164",
	165: "h165",
	166: "h166",
	167: "h167",
	168: "h168",
	169: "h169",
	170: "h170",
	171: "h171",
	172: "h172",
	173: "h173",
	174: "h174",
	175: "h175",
	176: "h176",
	177: "h177",
	178: "h178",
	179: "h179",
	180: "h180",
	181: "h181",
	182: "h182",
	183: "h183",
	184: "h184",
	185: "h185",
	186: "h186",
	187: "h187",
	188: "h188",
	189: "h189",
	190: "h190",
	191: "h191",
	192: "h192",
	193: "h193",
	194: "h194",
	195: "h195",
	196: "h196",
	197: "h197",
	198: "h198",
	199: "h199",
	200: "h200",
	201: "h201",
	202: "h202",
	203: "h203",
	204: "h204",
	205: "h205",
	206: "h206",
	207: "h207",
	208: "h208",
	209: "h209",
	210: "h210",
	211: "h211",
	212: "h212",
	213: "h213",
	214: "h214",
	215: "h215",
	216: "h216",
	217: "h217",
	218: "h218",
	219: "h219",
	220: "h220",
	221: "h221",
	222: "h222",
	223: "h223",
	224: "h224",
	225: "h225",
	226: "h226",
	227: "h227",
	228: "h228",
	229: "h229",
	230: "h230",
	231: "h231",
	232: "h232",
	233: "h233",
	234: "h234",
	235: "h235",
	236: "h236",
	237: "h237",
	238: "h238",
	239: "h239",
	240: "h240",
	241: "h241",
	242: "h242",
	243: "h243",
	244: "h244",
	245: "h245",
	246: "h246",
	247: "h247",
	248: "h248",
	249: "h249",
	250: "h250",
	251: "h251",
	252: "h252",
	253: "h253",
	254: "h254",
	255: "h255",
	256: "h256",
	257: "h257",
	258: "h258",
	259: "h259",
	260: "h260",
	261: "h261",
	262: "h262",
	263: "h263",
	264: "h264",
	265: "h265",
	266: "h266",
	267: "h267",
	268: "h268",
	269: "h269",
	270: "h270",
	271: "h271",
	272: "h272",
	273: "h273",
	274: "h274",
	275: "h275",
	276: "h276",
	277: "h277",
	278: "h278",
	279: "h279",
	280: "h280",
	281: "h281",
	282: "h282",
	283: "h283",
	284: "h284",
	285: "h285",
	286: "h286",
	287: "h287",
	288: "h288",
	289: "h289",
	290: "h290",
	291: "h291",
	292: "h292",
	293: "h293",
	294: "h294",
	295: "h295",
	296: "h296",
	297: "h297",
	298: "h298",
	299: "h299",
	300: "h300",
	301: "h301",
	302: "h302",
	303: "h303",
	304: "h304",
	305: "h305",
	306: "h306",
	307: "h307",
	308: "h308",
	309: "h309",
	310: "h310",
	311: "h311",
	312: "h312",
	313: "h313",
	314: "h314",
	315: "h315",
	316: "h316",
	317: "h317",
	318: "h318",
	319: "h319",
	320: "h320",
	321: "h321",
	322: "h322",
	323: "h323",
	324: "h324",
	325: "h325",
	326: "h326",
	327: "h327",
	328: "h328",
	329: "h329",
	330: "h330",
	331: "h331",
	332: "h332",
	333: "h333",
	334: "h334",
	335: "h335",
	336: "h336",
	337: "h337",
	338: "h338",
	339: "h339",
	340: "h340",
	341: "h341",
	342: "h342",
	343: "h343",
	344: "h344",
	345: "h345",
	346: "h346",
	347: "h347",
	348: "h348",
	349: "h349",
	350: "h350",
	351: "h351",
	352: "h352",
	353: "h353",
	354: "h354",
	355: "h355",
	356: "h356",
	357: "h357",
	358: "h358",
	359: "h359",
	360: "h360",
	361: "h361",
	362: "h362",
	363: "h363",
	364: "h364",
	365: "h365",
	366: "h366",
	367: "h367",
	368: "h368",
	369: "h369",
	370: "h370",
	371: "h371",
	372: "h372",
	373: "h373",
	374: "h374",
	375: "h375",
	376: "h376",
	377: "h377",
	378: "h378",
	379: "h379",
	380: "h380",
	381: "h381",
	382: "h382",
	383: "h383",
	384: "h384",
	385: "h385",
	386: "h386",
	387: "h387",
	388: "h388",
	389: "h389",
	390: "h390",
	391: "h391",
	392: "h392",
	393: "h393",
	394: "h394",
	395: "h395",
	396: "h396",
	397: "h397",
	398: "h398",
	399: "h399",
	400: "h400",
	401: "h401",
	402: "h402",
	403: "h403",
	404: "h404",
	405: "h405",
	406: "h406",
	407: "h407",
	408: "h408",
	409: "h409",
	410: "h410",
	411: "h411",
	412: "h412",
	413: "h413",
	414: "h414",
	415: "h415",
	416: "h416",
	417: "h417",
	418: "h418",
	419: "h419",
	420: "h420",
	421: "h421",
	422: "h422",
	423: "h423",
	424: "h424",
	425: "h425",
	426: "h426",
	427: "h427",
	428: "h428",
	429: "h429",
	430: "h430",
	431: "h431",
	432: "h432",
	433: "h433",
	434: "h434",
	435: "h435",
	436: "h436",
	437: "h437",
	438: "h438",
	439: "h439",
	440: "h440",
	441: "h441",
	442: "h442",
	443: "h443",
	444: "h444",
	445: "h445",
	446: "h446",
	447: "h447",
	448: "h448",
	449: "h449",
	450: "h450",
	451: "h451",
	452: "h452",
	453: "h453",
	454: "h454",
	455: "h455",
	456: "h456",
	457: "h457",
	458: "h458",
	459: "h459",
	460: "h460",
	461: "h461",
	462: "h462",
	463: "h463",
	464: "h464",
	465: "h465",
	466: "h466",
	467: "h467",
	468: "h468",
	469: "h469",
	470: "h470",
	471: "h471",
	472: "h472",
	473: "h473",
	474: "h474",
	475: "h475",
	476: "h476",
	477: "h477",
	478: "h478",
	479: "h479",
	480: "h480",
	481: "h481",
	482: "h482",
	483: "h483",
	484: "h484",
	485: "h485",
	486: "h486",
	487: "h487",
	488: "h488",
	489: "h489",
	490: "h490",
	491: "h491",
	492: "h492",
	493: "h493",
	494: "h494",
	495: "h495",
	496: "h496",
	497: "h497",
	498: "h498",
	499: "h499",
	500: "h500",
	501: "h501",
	502: "h502",
	503: "h503",
	504: "h504",
	505: "h505",
	506: "h506",
	507: "h507",
	508: "h508",
	509: "h509",
	510: "h510",
	511: "h511",
	512: "h512",
	513: "h513",
	514: "h514",
	515: "h515",
	516: "h516",
	517: "h517",
	518: "h518",
	519: "h519",
	520: "h520",
	521: "h521",
	522: "h522",
	523: "h523",
	524: "h524",
	525: "h525",
	526: "h526",
	527: "h527",
	528: "h528",
	529: "h529",
	530: "h530",
	531: "h531",
	532: "h532",
	533: "h533",
	534: "h534",
	535: "h535",
	536: "h536",
	537: "h537",
	538: "h538",
	539: "h539",
	540: "h540",
	541: "h541",
	542: "h542",
	543: "h543",
	544: "h544",
	545: "h545",
	546: "h546",
	547: "h547",
	548: "h548",
	549: "h549",
	550: "h550",
	551: "h551",
	552: "h552",
	553: "h553",
	554: "h554",
	555: "h555",
	556: "h556",
	557: "h557",
	558: "h558",
	559: "h559",
	560: "h560",
	561: "h561",
	562: "h562",
	563: "h563",
	564: "h564",
	565: "h565",
	566: "h566",
	567: "h567",
	568: "h568",
	569: "h569",
	570: "h570",
	571: "h571",
	572: "h572",
	573: "h573",
	574: "h574",
	575: "h575",
	576: "h576",
	577: "h577",
	578: "h578",
	579: "h579",
}
EOF_2
mkdir -p svc
cat > svc/svc.go <<'EOF_3'
// Package svc wires the api package into a running service.
package svc

import "example.com/mod/api"

// Service serves requests through a Router.
type Service struct {
	rtr *api.Router
}

func New(rtr *api.Router) *Service {
	return &Service{rtr: rtr}
}

// Lookup returns the handler name for path.
func (srv *Service) Lookup(path string) string {
	// call Match
	return srv.rtr.Match(path)
}
EOF_3
mkdir -p auth
cat > auth/auth.go <<'EOF_4'
// Package auth checks bearer tokens.
package auth

import "strings"

func Token(header string) string {
	return strings.TrimPrefix(header, "Bearer ")
}
EOF_4
mkdir -p cache
cat > cache/cache.go <<'EOF_5'
// Package cache holds values in memory.
package cache

// Cache maps keys to values.
type Cache struct {
	m map[string]string
}

func (cac *Cache) Set(k, v string) {
	cac.m[k] = v
}
EOF_5
mkdir -p config
cat > config/config.go <<'EOF_6'
// Package config reads key=value settings.
package config

import "strings"

func Parse(text string) map[string]string {
	out := map[string]string{}
	for _, line := range strings.Split(text, "\n") {
		k, v, _ := strings.Cut(line, "=")
		out[k] = v
	}
	return out
}
EOF_6
mkdir -p events
cat > events/events.go <<'EOF_7'
// Package events fans events out to subscribers.
package events

// Bus delivers events to subscribers.
type Bus struct {
	subs []chan string
}

// publish sends ev
func (bus *Bus) Publish(ev string) {
	for _, sub := range bus.subs {
		sub <- ev
	}
}
EOF_7
mkdir -p httpx
cat > httpx/httpx.go <<'EOF_8'
// Package httpx holds HTTP helpers.
package httpx

import "net/http"

func IsOK(resp *http.Response) bool {
	return resp.StatusCode >= 200 && resp.StatusCode < 300
}
EOF_8
mkdir -p logx
cat > logx/logx.go <<'EOF_9'
// Package logx formats log lines.
package logx

import "fmt"

func Line(level, msg string) string {
	return fmt.Sprintf("[%s] %s", level, msg)
}
EOF_9
mkdir -p metrics
cat > metrics/metrics.go <<'EOF_10'
// Package metrics counts events.
package metrics

// Counter counts events.
type Counter struct {
	n int
}

func (cnt *Counter) Inc() {
	// add one
	cnt.n++
}
EOF_10
mkdir -p queue
cat > queue/queue.go <<'EOF_11'
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Push appends v.
func (que *Queue) Push(v int) {
	que.items = append(que.items, v)
}
EOF_11
mkdir -p retry
cat > retry/retry.go <<'EOF_12'
// Package retry repeats a call until it succeeds.
package retry

func Do(n int, fn func() error) error {
	var err error
	for range n {
		if err = fn(); err == nil {
			return nil
		}
	}
	return err
}
EOF_12
