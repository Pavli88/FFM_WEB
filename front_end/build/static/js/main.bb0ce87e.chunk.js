(this.webpackJsonpffm_web_frontend=this.webpackJsonpffm_web_frontend||[]).push([[0],{109:function(e,t,n){},112:function(e,t,n){},121:function(e,t,n){"use strict";n.r(t);var c=n(0),r=n.n(c),a=n(35),i=n.n(a),s=(n(85),n(8)),o=(n(86),n(16)),l=n(20),j=r.a.createContext({environment:"live"}),d=n(5),b=n(18),h=n(19),O=n(1),u=function(e){var t=Object(c.useState)(e.defaultValue),n=Object(s.a)(t,2),r=n[0],a=n[1];return Object(O.jsx)(d.a,{children:Object(O.jsx)(d.a.Group,{style:{margin:"0px"},children:Object(O.jsxs)(b.a,{children:[Object(O.jsx)(h.a,{children:Object(O.jsx)(d.a.Label,{style:{verticalAlign:"middle"},children:r})}),Object(O.jsx)(h.a,{children:Object(O.jsx)(d.a.Control,{onChange:function(e){a(e.target.value)},type:"range",min:e.min,max:e.max,step:e.step,value:r})})]})})})},x=n(9),f=n(13),v=n.n(f),p=function(e){var t=Object(c.useState)(e.robot),n=Object(s.a)(t,2),r=n[0],a=(n[1],Object(c.useState)(e.dailyRisk)),i=Object(s.a)(a,2),o=i[0],l=i[1],j=Object(c.useState)(e.tradeLimit),d=Object(s.a)(j,2),b=d[0],h=d[1],f=Object(c.useState)(e.riskOnTrade),p=Object(s.a)(f,2),g=p[0],m=p[1],y=Object(c.useState)(e.pLevel),C=Object(s.a)(y,2),S=C[0],w=(C[1],Object(c.useState)(e.qType)),_=Object(s.a)(w,2),k=_[0],A=(_[1],Object(c.useState)(e.quantity)),L=Object(s.a)(A,2),E=L[0];L[1];return Object(O.jsxs)("tr",{children:[Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:r}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},onChange:function(e){l(e.target.value)},children:Object(O.jsx)(u,{defaultValue:o,min:0,max:.2,step:.005})}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},onChange:function(e){h(e.target.value)},children:Object(O.jsx)(u,{defaultValue:b,min:0,max:20,step:1})}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},onChange:function(e){m(e.target.value)},children:Object(O.jsx)(u,{defaultValue:g,min:0,max:.1,step:.0025})}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:S}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:k}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:E}),Object(O.jsx)("td",{children:Object(O.jsx)(x.a,{onClick:function(){v.a.post(e.server+"risk/update_robot_risk/",{robot:r,daily_risk:o,nbm_trades:b,risk_per_trade:g,pyramiding_level:S,quantity_type:k,quantity:E}).then((function(e){return console.log(e)})).catch((function(e){console.error("Error Message:",e)})),console.log(r),console.log(b),console.log(g)},children:"Update"})})]})},g=n(32),m=function(e){var t=Object(c.useContext)(j).environment,n=Object(c.useState)([]),r=Object(s.a)(n,2),a=r[0],i=r[1];Object(c.useEffect)((function(){fetch(e.server+"risk/get_robot_risk/"+t).then((function(e){return e.json()})).then((function(e){return i(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);var o=a.map((function(t){return Object(O.jsx)(p,{robot:t.robot,dailyRisk:t.daily_risk,tradeLimit:t.daily_trade_limit,riskOnTrade:t.risk_per_trade,pLevel:t.pyramiding_level,qType:t.quantity_type,quantity:t.quantity,server:e.server},t.id)}));return Object(O.jsxs)(g.a,{children:[Object(O.jsx)("thead",{style:{fontSize:12},children:Object(O.jsxs)("tr",{children:[Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Robot"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Daily Loss Limit %"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Max Number of Trades (Daily)"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Risk per Trade %"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Pyramiding Level"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Quantity Type"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Quantity"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"}})]})}),Object(O.jsx)("tbody",{children:o})]})},y=r.a.createContext(),C=function(){var e=Object(c.useContext)(y).server;return Object(O.jsx)(l.a,{className:"border",children:Object(O.jsx)(m,{server:e})})},S=n(14),w=(n(109),function(e){var t=Object(c.useState)([]),n=Object(s.a)(t,2),r=n[0],a=n[1];Object(c.useEffect)((function(){v.a.get(e.server+"home/load_robot_stats/"+e.env).then((function(e){return e.data})).then((function(e){return a(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);var i=r.map((function(e){return Object(O.jsxs)("tr",{children:[Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},className:"table-row-robot-name",children:e.robot.name}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},className:"table-row-other",children:e.balance}),Object(O.jsxs)("td",{style:{fontSize:12,verticalAlign:"middle"},className:"table-row-other",children:[e.dtd_ret," %"]}),Object(O.jsxs)("td",{style:{fontSize:12,verticalAlign:"middle"},className:"table-row-other",children:[e.mtd_ret," %"]}),Object(O.jsxs)("td",{style:{fontSize:12,verticalAlign:"middle"},className:"table-row-other",children:[e.ytd_ret," %"]})]},e.robot.id)}));return Object(O.jsx)(S.a,{className:"shadow-sm",style:{borderRadius:"0px"},children:Object(O.jsx)(S.a.Body,{style:{padding:"0px"},children:Object(O.jsxs)(g.a,{size:"sm",children:[Object(O.jsx)("thead",{children:Object(O.jsxs)("tr",{children:[Object(O.jsx)("th",{className:"table-row-robot-name",children:"Robot"}),Object(O.jsx)("th",{children:"Balance"}),Object(O.jsx)("th",{children:"DTD"}),Object(O.jsx)("th",{children:"MTD"}),Object(O.jsx)("th",{children:"YTD"})]})}),Object(O.jsx)("tbody",{children:i})]})})})}),_=n(79),k=n.n(_),A=function(e){var t={options:{chart:{toolbar:!1,id:"basic-bar"},xaxis:{categories:e.xdata,labels:{show:!1}},yaxis:[{labels:{formatter:function(e){return e.toFixed(0)}}}],dataLabels:{enabled:!1}},series:[{name:"series-1",data:e.ydata}]};return Object(O.jsx)(k.a,{options:t.options,series:t.series,type:e.chartType,width:"100%",height:"100%"})},L=function(e){var t={env:e.env,start_date:21,end_date:34},n=Object(c.useState)([]),r=Object(s.a)(n,2),a=r[0],i=r[1];Object(c.useEffect)((function(){v.a.get(e.server+"robots/get_robot_balance/"+e.env,{params:t}).then((function(e){return e.data})).then((function(e){return i(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);var o=Object(c.useState)([]),j=Object(s.a)(o,2),d=j[0],u=j[1];Object(c.useEffect)((function(){v.a.get(e.server+"risk/get_robot_risk/"+e.env).then((function(e){return e.data})).then((function(e){return u(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);var x={balance:a,risk:d};console.log(x);var f=a.map((function(e,t){return Object(O.jsxs)(S.a,{className:"shadow-sm",style:{marginTop:"5px",marginBottom:"5px",marginRight:"5px",height:"300px"},children:[Object(O.jsx)(S.a.Header,{as:"h6",children:e.robot}),Object(O.jsx)(S.a.Body,{style:{padding:"0px"},children:Object(O.jsx)(b.a,{style:{height:"100%",width:"100%",margin:"0px"},children:Object(O.jsx)(h.a,{style:{padding:"0px"},children:Object(O.jsx)(A,{chartType:"line",xdata:e.date,ydata:e.balance})})})})]},e.robot)}));return Object(O.jsx)(l.a,{className:"border",style:{padding:"0px",overflow:"scroll",height:"800px"},children:f})},E=(n(111),n(112),function(e){var t=Object(c.useContext)(j).environment,n=Object(c.useContext)(y).server;return Object(O.jsx)(l.a,{style:{background:"#FBFAFA",width:"100%",height:window.innerHeight},fluid:!0,children:Object(O.jsxs)(b.a,{style:{height:window.innerHeight},children:[Object(O.jsx)(h.a,{style:{height:"100%"},children:Object(O.jsxs)(l.a,{children:[Object(O.jsx)(b.a,{style:{margin:"5px"},children:Object(O.jsx)("h5",{style:{textAlign:"center",width:"100%",margin:"0px"},children:"Robots"})}),Object(O.jsx)(L,{env:t,server:n})]})}),Object(O.jsxs)(h.a,{style:{height:"100%"},children:[Object(O.jsxs)(l.a,{children:[Object(O.jsx)(b.a,{style:{margin:"5px"},children:Object(O.jsx)("h5",{style:{textAlign:"center",width:"100%",margin:"0px"},children:"Performance"})}),Object(O.jsx)(w,{server:n,env:t})]}),Object(O.jsxs)(l.a,{children:[Object(O.jsx)(b.a,{style:{margin:"5px"},children:Object(O.jsx)("h5",{style:{textAlign:"center",width:"100%",margin:"0px"},children:"Accounts"})}),Object(O.jsx)(b.a,{style:{height:"400px",paddingTop:"5px",paddingBottom:"5px"},children:Object(O.jsx)(h.a,{style:{paddingLeft:"5px",paddingRight:"5px"},children:Object(O.jsx)(S.a,{style:{height:"100%",width:"100%",margin:"0px"}})})})]})]})]})})}),N=r.a.createContext(),F=n(10),T=function(e){var t=Object(c.useState)(""),n=Object(s.a)(t,2),r=n[0],a=n[1],i=Object(c.useState)(""),o=Object(s.a)(i,2),l=o[0],j=o[1],b=Object(c.useState)("Trade"),h=Object(s.a)(b,2),u=h[0],f=h[1],p=Object(c.useState)("USD"),g=Object(s.a)(p,2),m=g[0],y=g[1],C=Object(c.useState)(!1),S=Object(s.a)(C,2),w=S[0],_=S[1],k=function(){return _(!1)};console.log(r,u,m);var A=function(t){t.preventDefault(),v.a.post(e.server+"portfolios/new/",{port_name:r,port_type:u,port_currency:m,port_code:l}).then((function(e){"New Portfolio was created!"==e.data?window.location.reload():alert(e.data)})).catch((function(e){console.error("Error Message:",e)})),_(!1)};return Object(O.jsxs)(O.Fragment,{children:[Object(O.jsx)(x.a,{variant:"primary",onClick:function(){return _(!0)},children:"New Portfolio"}),Object(O.jsxs)(F.a,{show:w,onHide:k,children:[Object(O.jsx)(F.a.Header,{closeButton:!0,children:Object(O.jsx)(F.a.Title,{children:"New Portfolio"})}),Object(O.jsx)(F.a.Body,{children:Object(O.jsxs)(d.a,{onSubmit:A,style:{width:"100%"},children:[Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio Name"}),Object(O.jsx)(d.a.Control,{onChange:function(e){a(e.target.value)},type:"text",placeholder:"Portfolio Name",required:!0})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio Code"}),Object(O.jsx)(d.a.Control,{onChange:function(e){j(e.target.value)},type:"text",placeholder:"Portfolio Code",required:!0})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio Type"}),Object(O.jsxs)(d.a.Control,{onChange:function(e){f(e.target.value)},as:"select",children:[Object(O.jsx)("option",{value:"Trade",children:"Trade"}),Object(O.jsx)("option",{value:"Savings",children:"Savings"}),Object(O.jsx)("option",{value:"Investment",children:"Investment"})]})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio Currency"}),Object(O.jsxs)(d.a.Control,{onChange:function(e){y(e.target.value)},as:"select",children:[Object(O.jsx)("option",{value:"USD",children:"USD"}),Object(O.jsx)("option",{value:"HUF",children:"HUF"}),Object(O.jsx)("option",{value:"EUR",children:"EUR"})]})]})]})}),Object(O.jsxs)(F.a.Footer,{children:[Object(O.jsx)(x.a,{variant:"secondary",onClick:k,children:"Close"}),Object(O.jsx)(x.a,{variant:"primary",onClick:A,children:"Save"})]})]})]})},B=function(e){var t=Object(c.useState)([]),n=Object(s.a)(t,2),r=n[0],a=n[1];return Object(c.useEffect)((function(){v.a.get(e.server+"portfolios/get_portfolio_data/").then((function(e){return e.data.map((function(e){return Object(O.jsxs)("tr",{children:[Object(O.jsx)("td",{className:"table-row-robot-name",children:e.portfolio_name}),Object(O.jsx)("td",{className:"table-row-other",children:e.portfolio_type}),Object(O.jsx)("td",{className:"table-row-other",children:e.currency}),Object(O.jsx)("td",{className:"table-row-other",children:e.inception_date}),Object(O.jsx)("td",{className:"table-row-other",children:e.status})]},e.id)}))})).then((function(e){return a(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]),Object(O.jsxs)(g.a,{children:[Object(O.jsx)("thead",{children:Object(O.jsxs)("tr",{children:[Object(O.jsx)("th",{className:"table-row-robot-name",children:"Portfolio"}),Object(O.jsx)("th",{children:"Portfolio Type"}),Object(O.jsx)("th",{children:"Currency"}),Object(O.jsx)("th",{children:"Inception Date"}),Object(O.jsx)("th",{children:"Status"})]})}),Object(O.jsx)("tbody",{children:r})]})},D=function(e){var t=Object(c.useState)(""),n=Object(s.a)(t,2),r=n[0],a=n[1];return Object(c.useEffect)((function(){v.a.get(e.url,{params:e.params}).then((function(t){return t.data.map((function(t){return Object(O.jsx)("option",{value:t[e.code],children:t[e.value]},t.id)}))})).then((function(e){return a(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]),r},P=function(e){var t=Object(c.useState)(!1),n=Object(s.a)(t,2),r=n[0],a=n[1],i=Object(c.useState)(""),o=Object(s.a)(i,2),l=o[0],j=o[1],b=Object(c.useState)(""),h=Object(s.a)(b,2),u=h[0],f=h[1],p=Object(c.useState)(0),g=Object(s.a)(p,2),m=g[0],y=g[1];console.log(l);var C=function(){return a(!1)},S=function(t){t.preventDefault(),console.log("form submited"),v.a.post(e.server+"portfolios/portfolio_trade/",{portfolio:e.portfolio,unit:m,sec:u,sec_type:"Robot",sec_id:l}).then((function(e){return alert(e.data)})).catch((function(e){console.error("Error Message:",e)})),a(!1)};return Object(O.jsxs)(O.Fragment,{children:[Object(O.jsx)(x.a,{variant:"primary",onClick:function(){return a(!0)},children:"BUY"}),Object(O.jsxs)(F.a,{show:r,onHide:C,children:[Object(O.jsx)(F.a.Header,{closeButton:!0,children:Object(O.jsx)(F.a.Title,{children:"Buy"})}),Object(O.jsx)(F.a.Body,{children:Object(O.jsxs)(d.a,{onSubmit:S,style:{width:"100%"},children:[Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio"}),Object(O.jsx)(d.a.Control,{type:"text",placeholder:e.portfolio,value:e.portfolio,readOnly:!0})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Robot"}),Object(O.jsx)(d.a.Control,{onChange:function(e){var t=e.nativeEvent.target.selectedIndex;j(e.target.value),f(e.nativeEvent.target[t].text)},as:"select",children:Object(O.jsx)(D,{url:e.server+"instruments/get_instruments/",params:{type:"Robot"},code:"id",value:"instrument_name"})})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Unit"}),Object(O.jsx)(d.a.Control,{onChange:function(e){y(e.target.value)},type:"number",min:0})]})]})}),Object(O.jsxs)(F.a.Footer,{children:[Object(O.jsx)(x.a,{variant:"secondary",onClick:C,children:"Close"}),Object(O.jsx)(x.a,{variant:"primary",onClick:S,children:"Save"})]})]})]})},R=function(e){var t=Object(c.useState)(!1),n=Object(s.a)(t,2),r=n[0],a=n[1],i=function(){return a(!1)},o=Object(c.useState)(0),l=Object(s.a)(o,2),j=l[0],b=l[1],h=Object(c.useState)("TRADE"),u=Object(s.a)(h,2),f=u[0],p=u[1],g=Object(c.useState)("USD"),m=Object(s.a)(g,2),y=m[0],C=m[1],S=function(t){t.preventDefault(),console.log("form submited"),v.a.post(e.server+"portfolios/new_cash_flow/",{port_name:e.portfolio,amount:j,type:f,currency:y}).then((function(e){return alert(e.data)})).catch((function(e){console.error("Error Message:",e)})),a(!1)};return Object(O.jsxs)(O.Fragment,{children:[Object(O.jsx)(x.a,{variant:"primary",onClick:function(){return a(!0)},children:"Add Cash"}),Object(O.jsxs)(F.a,{show:r,onHide:i,children:[Object(O.jsx)(F.a.Header,{closeButton:!0,children:Object(O.jsx)(F.a.Title,{children:"New Cash Flow"})}),Object(O.jsx)(F.a.Body,{children:Object(O.jsxs)(d.a,{onSubmit:S,style:{width:"100%"},children:[Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Portfolio"}),Object(O.jsx)(d.a.Control,{type:"text",placeholder:e.portfolio,value:e.portfolio,readOnly:!0})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Cash Flow"}),Object(O.jsx)(d.a.Control,{onChange:function(e){b(e.target.value)},type:"number",placeholder:"Value"})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Currency"}),Object(O.jsxs)(d.a.Control,{onChange:function(e){C(e.target.value)},as:"select",children:[Object(O.jsx)("option",{value:"USD",children:"USD"}),Object(O.jsx)("option",{value:"EUR",children:"EUR"})]})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Type"}),Object(O.jsx)(d.a.Control,{onChange:function(e){p(e.target.value)},as:"select",children:Object(O.jsx)("option",{value:"INFLOW",children:"Inflow"})})]})]})}),Object(O.jsxs)(F.a.Footer,{children:[Object(O.jsx)(x.a,{variant:"secondary",onClick:i,children:"Close"}),Object(O.jsx)(x.a,{variant:"primary",onClick:S,children:"Save"})]})]})]})},H=function(){return Object(O.jsxs)(S.a,{style:{height:"200px"},children:[Object(O.jsx)("div",{style:{display:"flex",width:"50%"},children:Object(O.jsx)(S.a.Title,{children:"Settings"})}),Object(O.jsx)("h2",{children:"Price source"})]})},G=function(){return Object(O.jsx)(S.a,{style:{height:"200px"},children:Object(O.jsx)("div",{style:{display:"flex",width:"50%"},children:Object(O.jsx)(S.a.Title,{children:"Holdings"})})})},M=function(e){var t=Object(c.useContext)(y).server,n=(Object(c.useContext)(j).environment,Object(c.useContext)(N).portfolioData),r=Object(c.useState)(n[0].portfolio_code),a=Object(s.a)(r,2),i=a[0],o=a[1];console.log(n);var u=n.map((function(e){return Object(O.jsx)("option",{value:e.portfolio_code,children:e.portfolio_name},e.id)}));return Object(O.jsx)(l.a,{style:{background:"#FBFAFA",width:"100%",height:window.innerHeight,padding:"20px"},fluid:!0,children:Object(O.jsxs)(b.a,{children:[Object(O.jsx)(h.a,{children:Object(O.jsxs)(l.a,{className:"border",style:{width:"100%",height:window.innerHeight},children:[Object(O.jsx)(S.a,{style:{height:"200px"},children:Object(O.jsxs)("div",{style:{display:"flex",width:"50%"},children:[Object(O.jsx)(S.a.Title,{children:"Portfolio"}),Object(O.jsx)(d.a.Control,{onChange:function(e){o(e.target.value)},as:"select",children:u})]})}),Object(O.jsxs)(S.a,{style:{height:"200px"},children:[Object(O.jsx)(R,{portfolio:i,server:t}),Object(O.jsx)(P,{portfolio:i,server:t})]}),Object(O.jsx)(G,{})]})}),Object(O.jsxs)(h.a,{children:[Object(O.jsx)(l.a,{className:"border",style:{height:"50%"},children:Object(O.jsx)(T,{server:t})}),Object(O.jsxs)(S.a,{children:[Object(O.jsx)(S.a.Header,{as:"h5"}),Object(O.jsx)(B,{server:t})]}),Object(O.jsx)(H,{})]})]})})},z=function(e){return Object(O.jsxs)("tr",{children:[Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:e.id}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:e.broker_id}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:e.security}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:e.robot}),Object(O.jsx)("td",{style:{fontSize:12,verticalAlign:"middle"},children:e.quantity}),Object(O.jsx)("td",{children:Object(O.jsx)(x.a,{onClick:function(){v.a.post(e.server+"trade_page/close_trade/",{broker_id:e.broker_id,robot:e.robot,trd_id:e.id}).then((function(e){return alert(e.data)})).catch((function(e){console.error("Error Message:",e)}))},children:"Close"})})]})},I=function(e){var t=Object(c.useState)([]),n=Object(s.a)(t,2),r=n[0],a=n[1];Object(c.useEffect)((function(){fetch(e.server+"trade_page/get_open_trades/"+e.env).then((function(e){return e.json()})).then((function(e){return a(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);var i=r.map((function(t){return Object(O.jsx)(z,{server:e.server,id:t.id,broker_id:t.broker_id,security:t.security,robot:t.robot,quantity:t.quantity},t.id)}));return Object(O.jsx)(S.a,{style:{width:"100%"},children:Object(O.jsxs)(g.a,{children:[Object(O.jsx)("thead",{style:{fontSize:12},children:Object(O.jsxs)("tr",{children:[Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Platform ID"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Broker ID"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Security"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Robot"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"},children:"Quantity"}),Object(O.jsx)("th",{style:{verticalAlign:"middle"}})]})}),Object(O.jsx)("tbody",{style:{height:"100%",overflow:"scroll"},children:i})]})})},U=function(){var e=Object(c.useContext)(y).server,t=Object(c.useContext)(j).environment;return Object(O.jsxs)(l.a,{className:"border",style:{background:"#FBFAFA",width:"100%",height:window.innerHeight,padding:"20px"},fluid:!0,children:[Object(O.jsx)(b.a,{style:{height:"60%",background:"green"}}),Object(O.jsx)(b.a,{style:{height:"40%",background:"blue"},children:Object(O.jsx)(I,{env:t,server:e})})]})},q=n(127),V=n(128),Q=(n(113),n(55)),Y=n(25),J=n(49),K=n(36),W=function(e){return Object(O.jsxs)(q.a,{bg:"dark",variant:"dark",children:[Object(O.jsx)(q.a.Brand,{href:"#home",children:"FFM SYSTEM"}),Object(O.jsxs)(V.a,{className:"mr-auto",children:[Object(O.jsx)(V.a.Link,{as:K.b,to:"/home",children:"Home"}),Object(O.jsx)(V.a.Link,{as:K.b,to:"/portfolio",children:"Portfolio"}),Object(O.jsx)(V.a.Link,{as:K.b,to:"/robot",children:"Robot"}),Object(O.jsx)(V.a.Link,{as:K.b,to:"/risk",children:"Risk"}),Object(O.jsx)(V.a.Link,{as:K.b,to:"/instruments",children:"Instrument"}),Object(O.jsx)(V.a.Link,{as:K.b,to:"/trade",children:"Trade"}),Object(O.jsxs)(J.a,{title:"Calculations",children:[Object(O.jsx)(J.a.Item,{children:"Robot Balance"}),Object(O.jsx)(J.a.Item,{}),Object(O.jsx)(J.a.Divider,{}),Object(O.jsx)(J.a.Item,{children:"Portfolio Holdings"})]})]}),Object(O.jsxs)(d.a,{inline:!0,children:[Object(O.jsx)(Q.a,{type:"text",placeholder:"Search",className:"mr-sm-2"}),Object(O.jsx)(x.a,{variant:"outline-info",children:"Search"})]}),Object(O.jsxs)(Y.a,{onSelect:function(t){e.onEnvChange(t)},style:{marginLeft:"10px"},children:[Object(O.jsx)(Y.a.Toggle,{variant:"success",id:"dropdown-basic",children:"Environment"}),Object(O.jsxs)(Y.a.Menu,{children:[Object(O.jsx)(Y.a.Item,{eventKey:"live",children:"Live"}),Object(O.jsx)(Y.a.Item,{eventKey:"demo",children:"Demo"})]})]})]})},X=function(e){var t=Object(c.useState)(""),n=Object(s.a)(t,2),r=(n[0],n[1]),a=Object(c.useState)(""),i=Object(s.a)(a,2),o=(i[0],i[1]),l=Object(c.useState)("oanda"),j=Object(s.a)(l,2),b=j[0],h=j[1],u=Object(c.useState)("live"),f=Object(s.a)(u,2),v=f[0],p=f[1],g=Object(c.useState)(""),m=Object(s.a)(g,2),y=m[0],C=m[1],S=Object(c.useState)(""),w=Object(s.a)(S,2),_=w[0],k=w[1];console.log(y),console.log(_);var A=Object(c.useState)(!1),L=Object(s.a)(A,2),E=L[0],N=L[1],T=function(){return N(!1)},B={broker:b,env:v},P={broker:b},R=function(e){e.preventDefault()};return Object(c.useEffect)((function(){}),[]),Object(O.jsxs)(O.Fragment,{children:[Object(O.jsx)(x.a,{variant:"primary",onClick:function(){return N(!0)},children:"New Robot"}),Object(O.jsxs)(F.a,{show:E,onHide:T,children:[Object(O.jsx)(F.a.Header,{closeButton:!0,children:Object(O.jsx)(F.a.Title,{children:"New Robot"})}),Object(O.jsx)(F.a.Body,{children:Object(O.jsxs)(d.a,{onSubmit:R,style:{width:"100%"},children:[Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Robot Name"}),Object(O.jsx)(d.a.Control,{onChange:function(e){r(e.target.value)},type:"text",placeholder:"Robot Name"})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Strategy"}),Object(O.jsx)(d.a.Control,{onChange:function(e){o(e.target.value)},type:"text"})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Broker"}),Object(O.jsxs)(d.a.Control,{onChange:function(e){h(e.target.value)},as:"select",children:[Object(O.jsx)("option",{children:"oanda"}),Object(O.jsx)("option",{children:"Fix"})]})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Environment"}),Object(O.jsxs)(d.a.Control,{onChange:function(e){p(e.target.value)},as:"select",children:[Object(O.jsx)("option",{value:"live",children:"Live"}),Object(O.jsx)("option",{value:"demo",children:"Demo"})]})]}),Object(O.jsx)(D,{}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Instruments"}),Object(O.jsx)(d.a.Control,{onChange:function(e){k(e.target.value)},as:"select",children:Object(O.jsx)(D,{url:e.server+"instruments/get_instruments/",params:P,code:"instrument_name",value:"instrument_name"})})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Account Number"}),Object(O.jsx)(d.a.Control,{onChange:function(e){C(e.target.value)},as:"select",value:y,children:Object(O.jsx)(D,{url:e.server+"accounts/get_accounts_data/",params:B,code:"account_number",value:"account_number"})})]})]})}),Object(O.jsxs)(F.a.Footer,{children:[Object(O.jsx)(x.a,{variant:"secondary",onClick:T,children:"Close"}),Object(O.jsx)(x.a,{variant:"primary",onClick:R,children:"Save"})]})]})]})},Z=function(e){var t=e.list.map((function(e){return Object(O.jsx)("td",{children:e})}));return Object(O.jsx)("thead",{children:Object(O.jsx)("tr",{children:t})})},$=function(e){var t=Object(c.useState)(new Date),n=Object(s.a)(t,2),r=n[0],a=n[1],i=Object(c.useState)(new Date),o=Object(s.a)(i,2),l=o[0],j=o[1],b=Object(c.useState)("ALL"),h=Object(s.a)(b,2),u=h[0],f=h[1],p=Object(c.useState)(!1),g=Object(s.a)(p,2),m=g[0],y=g[1];console.log(r),console.log(l);var C=function(t){t.preventDefault(),y(!0),v.a.post(e.server+"robots/process_hub/",{process:"Balance",robot:u,start_date:r,end_date:l}).then((function(e){return y(!1)})).catch((function(e){console.error("Error Message:",e)}))};return Object(O.jsxs)(S.a,{children:[Object(O.jsx)(S.a.Header,{as:"h5",children:"Balance Calculator"}),Object(O.jsx)(S.a.Body,{children:Object(O.jsxs)(d.a,{onSubmit:C,style:{width:"100%"},children:[Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Start Date"}),Object(O.jsx)(d.a.Control,{onChange:function(e){a(e.target.value)},type:"date"})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"End Date"}),Object(O.jsx)(d.a.Control,{onChange:function(e){j(e.target.value)},type:"date"})]}),Object(O.jsxs)(d.a.Group,{children:[Object(O.jsx)(d.a.Label,{children:"Robots"}),Object(O.jsx)(d.a.Control,{onChange:function(e){f(e.target.value)},as:"select",children:Object(O.jsx)("option",{value:"ALL",children:"ALL"})})]}),Object(O.jsx)(x.a,{variant:"primary",onClick:C,children:"Calculate"})]})}),Object(O.jsx)(F.a,{show:m,children:Object(O.jsx)(F.a.Body,{style:{width:"200px",height:"300px"},children:Object(O.jsx)("h2",{children:"Calculating ..."})})})]})},ee=function(e){Object(c.useContext)(j).environment;return Object(O.jsxs)("tr",{children:[Object(O.jsx)("td",{children:e.data.name}),Object(O.jsx)("td",{children:e.data.strategy}),Object(O.jsx)("td",{children:e.data.security}),Object(O.jsx)("td",{children:e.data.broker}),Object(O.jsx)("td",{children:e.data.env}),Object(O.jsx)("td",{children:e.data.status}),Object(O.jsx)("td",{children:e.data.account_number}),Object(O.jsx)("td",{children:Object(O.jsx)(x.a,{onClick:function(){console.log("Button Clicked")},children:"Update"})})]})},te=function(e){var t=Object(c.useContext)(y).server,n=Object(c.useContext)(j).environment,r=Object(c.useState)([]),a=Object(s.a)(r,2),i=a[0],o=a[1];Object(c.useEffect)((function(){v.a.get(t+"robots/get_robots/"+n).then((function(e){return e.data.map((function(e){return Object(O.jsx)(ee,{data:e},e.id)}))})).then((function(e){return o(e)})).catch((function(e){console.error("Error Message:",e)}))}),[e]);return Object(O.jsx)(l.a,{style:{background:"#FBFAFA",width:"100%",height:window.innerHeight,padding:"20px"},fluid:!0,children:Object(O.jsxs)(b.a,{children:[Object(O.jsx)(h.a,{children:Object(O.jsxs)(S.a,{children:[Object(O.jsx)(S.a.Header,{as:"h5",children:Object(O.jsx)(X,{server:t,style:{height:"400px"}})}),Object(O.jsxs)(g.a,{children:[Object(O.jsx)(Z,{list:["Name","Strategy","Security","Broker","Env","Status","Account Number",""]}),Object(O.jsx)("tbody",{children:i})]})]})}),Object(O.jsx)(h.a,{children:Object(O.jsx)($,{server:t})})]})})},ne=function(){return Object(O.jsx)("div",{children:Object(O.jsx)("h2",{children:"Instrument Page"})})};var ce=function(){var e=Object(c.useState)("live"),t=Object(s.a)(e,2),n=t[0],r=t[1],a="https://pavliati.pythonanywhere.com/",i=Object(c.useState)([]),l=Object(s.a)(i,2),d=l[0],b=l[1];return Object(c.useEffect)((function(){v.a.get(a+"portfolios/get_portfolio_data/").then((function(e){return b(e.data)})).catch((function(e){console.error("Error Message:",e)}))}),[]),Object(O.jsx)(y.Provider,{value:{server:a},children:Object(O.jsx)(j.Provider,{value:{environment:n},children:Object(O.jsx)(N.Provider,{value:{portfolioData:d},children:Object(O.jsxs)("div",{className:"App",children:[Object(O.jsx)(W,{onEnvChange:function(e){r(e)}}),Object(O.jsxs)(o.c,{children:[Object(O.jsx)(o.a,{path:"/risk",children:Object(O.jsx)(C,{})}),Object(O.jsx)(o.a,{path:"/home",children:Object(O.jsx)(E,{})}),Object(O.jsx)(o.a,{path:"/trade",children:Object(O.jsx)(U,{})}),Object(O.jsx)(o.a,{path:"/portfolio",children:Object(O.jsx)(M,{})}),Object(O.jsx)(o.a,{path:"/instruments",children:Object(O.jsx)(ne,{})}),Object(O.jsx)(o.a,{path:"/robot",children:Object(O.jsx)(te,{})})]})]})})})})},re=function(e){e&&e instanceof Function&&n.e(3).then(n.bind(null,129)).then((function(t){var n=t.getCLS,c=t.getFID,r=t.getFCP,a=t.getLCP,i=t.getTTFB;n(e),c(e),r(e),a(e),i(e)}))};i.a.render(Object(O.jsx)(r.a.StrictMode,{children:Object(O.jsx)(K.a,{children:Object(O.jsx)(ce,{})})}),document.getElementById("root")),re()},85:function(e,t,n){},86:function(e,t,n){}},[[121,1,2]]]);
//# sourceMappingURL=main.bb0ce87e.chunk.js.map