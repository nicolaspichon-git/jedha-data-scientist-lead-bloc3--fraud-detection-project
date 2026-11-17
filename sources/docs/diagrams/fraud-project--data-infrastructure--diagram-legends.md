---
version: v15
locale: en
---

###### Links
```mermaid
flowchart
	LGA["A"] -->|"data flow"| LGB["B"]
	LGC["A"] ==>|"control flow"| LGD["B"]
	LGE["A"] -.->|"dependency"| LGF["B"]
```

###### Colors

Three families of group, and two node styles that override the group hue.

| Family | Treatment | Why |
|---|---|---|
| **Pipelines** carrying transaction data | one of four validated hues | they are the actors |
| **Data layers** | neutral, warm *vs* cool | they are a substrate, not an actor |
| **Cross-cutting groups** | neutral grey, most recessive | they belong to no pipeline |

`Data Retention` is a pipeline, yet it is shown neutral: the four hues are reserved for the
pipelines that carry transaction data, and a fifth hue would fail colour-vision validation.

```mermaid
flowchart
	subgraph HDL["Historical Data Loading"]
		H1["box"]
	end
	subgraph G1["Transactions Ingestion"]
		I1["box"]
	end
	subgraph MT["Models Training"]
		M1["box"]
	end
	subgraph G2["Daily Reporting"]
		D1["box"]
	end
	subgraph PURGE["Data Retention"]
		P1["box"]
	end
	subgraph BRONZE["Bronze"]
		B1[("as received")]
	end
	subgraph SILVER["Silver"]
		S1[("typed + validated")]
	end
	subgraph META["Metadata"]
		E1[("runs, models")]
	end
	
	subgraph OVR["Overrides the group hue"]
		SH[("<b>shared store or policy</b><br/>written and/or read<br/>by more than one pipeline")]
		DM("<b>simulation parameter</b><br/>absent from a real deployment")
	end
	
    SILVER ~~~ OVR
    
    %% pipelines carrying transaction data : four validated hues
    style HDL    fill:#f2e9f6,stroke:#7b1fa2,stroke-width:2px
    style G1     fill:#eaf2fb,stroke:#2a78d6,stroke-width:2px
    style MT     fill:#fdf0eb,stroke:#eb6834,stroke-width:2px
    style G2     fill:#e8f7f2,stroke:#1baf7a,stroke-width:2px
    %% data layers : neutral, warm vs cool
    style BRONZE fill:#f7f1e6,stroke:#8a6a3c,stroke-width:2px
    style SILVER fill:#eef0f2,stroke:#78808a,stroke-width:2px
    %% cross-cutting : neutral grey
    style META   fill:#fafaf9,stroke:#b9b9b2,stroke-width:2px
    style PURGE  fill:#fafaf9,stroke:#8d8d86,stroke-width:2px
    style OVR    fill:#fafaf9,stroke:#b9b9b2,stroke-width:1.5px

    classDef nHDL fill:#dac0e5,stroke:#7b1fa2,stroke-width:1.5px,color:#111111
    classDef nG1  fill:#c3d9f4,stroke:#2a78d6,stroke-width:1.5px,color:#111111
    classDef nMT  fill:#f9d5c6,stroke:#eb6834,stroke-width:1.5px,color:#111111
    classDef nG2  fill:#bfe9da,stroke:#1baf7a,stroke-width:1.5px,color:#111111
    classDef nPURGE fill:#e8e8e5,stroke:#8d8d86,stroke-width:1.5px,color:#111111
    class H1 nHDL
    class I1 nG1
    class M1 nMT
    class D1 nG2
    class P1 nPURGE

    classDef shared fill:#ffffff,stroke:#2b2b2b,stroke-width:2.5px,color:#111111
    class B1,S1,E1,SH shared
    classDef demo fill:#ffffff,stroke:#8a6a3c,stroke-width:1.5px,stroke-dasharray:4 3,color:#333333
    class DM demo
```

> Bronze, Silver and Metadata hold shared elements only, so no box inside them carries a group
> hue : **coloured = belongs to one pipeline · white = crossed by several**.
> The four hues were validated for colour-vision deficiency (worst pair ΔE 9.2 in deuteranopia,
> 21.5 in normal vision). Group titles always name the group, so colour never carries the
> information alone.

###### Shapes
```mermaid
flowchart
   SH3(["<b>timer : starts a run</b><br/>⏱ every minute<br/>▶ manual"])
	SH1{{"<b>pipeline : code that executes and transforms</b><br/>dag_ingest : process"}}
	SH2[("<b>data storage : state that survives the run</b><br/>raw_events<br/>transactions<br/>datasets")]
	SH4("<b>registry/metadata/configuration</b><br/>models registry<br/>decision policy")
	SH5["<b>input/output : system's boundary</b><br/>realtime API<br/>outbound channel<br/>daily report"]

    classDef neutral fill:#f4f4f2,stroke:#8d8d86,stroke-width:1.5px,color:#111111
    class SH1,SH2,SH3,SH4,SH5 neutral
```
