;(function(){
  "use strict";

  requirejs.config({
    paths: {
      d3: "/nbextensions/nbmonty/bower_components/d3/d3.min",
      jsonld: "/nbextensions/nbmonty/bower_components/jsonld.js/js/jsonld"
    },
    shim: {
      jsonld: {
        exports: "jsonld"
      }
    }
  });

  define(
    [
      "widgets/js/widget",
      "underscore", "d3",
      "jsonld"
    ],

    function(widgets, _, d3, jsonld){
      var HorizonsView = widgets.DOMWidgetView.extend({
        className: "nb-monty HorizonsView",

        render: function(options){
          var view = this;

          this.d3 = d3.select(this.el);

          this.listenTo(this.model, {
            "change:nodes": this.changeNodes,
            "change:horizons": this.changeHorizons,
            "change:height": this.resize,
            "change:width": this.resize,
            "change:x_scale": this.resize,
            "change:y_scale": this.resize,
            "change:title": this.chrome
          });

          this.svg = this.d3.selectAll("svg").data([1])
            .call(function(init){
              init.enter().append("svg");
            });

          this.margin = {
            title: -20,
            top: 50,
            right: 30,
            bottom: 30,
            left: 40
          };

          this.root = this.svg.selectAll("g").data([1])
            .call(function(init){
              init.enter().append("g")
                .classed({"root": 1});
            });

          this.scales = {};

          var x = this.scales.x = d3.time.scale(),
            y = this.scales.y = d3.scale.linear();

          this.drag = d3.behavior.drag()
            .on("drag", function(d) {
              d.x = x.invert(d3.event.x);
              d.y = y.invert(d3.event.y);

              view.positionCards(d3.select(this))
            })
            .on("dragend", function(){
              view.touch();
            });


          this.axes = {
            x: d3.svg.axis()
              .scale(x)
              .orient("bottom"),
            y: d3.svg.axis()
              .scale(y)
              .orient("left")
          };

          _.defer(_.bind(this.resize, this));
        },

        chrome: function(){
          this.root.selectAll(".chart-title").data([1])
            .call(function(init){
              init.enter().append("text")
                .attr({
                  "text-anchor": "middle"
                })
                .classed({
                  "chart-title": 1
                });
            })
            .text(this.model.get("title"))
            .attr({
              "x": this.el.clientWidth / 2,
              "y": this.margin.title
            });

          this.root.selectAll(".x.axis").data([1])
            .call(function(init){
              init.enter().append("g").attr("class", "x axis");
            })
            .attr("transform", "translate(0," + this.scales.y.range()[1] + ")")
            .call(this.axes.x);


          this.root.selectAll(".y.axis").data([1])
            .call(function(init){
              init.enter().append("g").attr("class", "y axis");
            })
            .call(this.axes.y);

          return this;
        },

        touch: function(){
          this.model.set("ld", JSON.stringify(this.model.get("nodes")));
          return HorizonsView.__super__.touch.apply(this, arguments);
        },

        getter: function(attr){
          return function(d){ return d[attr]; }
        },

        resize: function(){
          this.scales.x
            .domain(_.map(this.model.get("x_scale"), function(d){
              return new Date(d);
            }))
            .range([
              0,
              this.el.clientWidth - (this.margin.right + this.margin.left)
            ]);
          this.scales.y
            .domain(this.model.get("y_scale"))
            .range([
              0,
              this.el.clientHeight - (this.margin.top + this.margin.bottom)
            ]);

          this.chrome();

          this.svg.attr({
            width: this.el.clientWidth,
            height: this.el.clientHeight
          });

          this.root.attr("transform", "translate(" + [
            this.margin.left, this.margin.top
          ] +")");

          return this;
        },

        positionCards: function(card){
          var x = this.scales.x,
            y = this.scales.y;
          (card || this.card).attr({
            transform: function(d){
              return "translate(" + [x(d.x), y(d.y)] + ")";
            }
          });
          return this;
        },

        changeHorizons: function(){
          var view = this,
            horizons = this.root.selectAll(".horizons").data([1])
              .call(function(init){
                init.enter().append("g").classed({cards: 1});
              }),
            horizon = horizons.selectAll(".horizon")
              .data(this.model.get("horizons"));


            horizon.enter().append("g")
              .classed({horizon: 1})
              .call(function(init){
                init.append("path");
              });
        },

        changeNodes: function(){
          var view = this,
            cards = this.root.selectAll(".cards").data([1])
              .call(function(init){
                init.enter().append("g").classed({cards: 1});
              }),
            card = this.card = cards.selectAll(".card")
              .data(this.model.get("nodes"));

          card.enter().append("g")
            .classed({card: 1})
            .call(function(init){
              init.append("rect").attr({
                width: 250,
                height: 150
              });
              init.append("text")
                .attr({
                  dy:".35em",
                  "text-anchor": "middle",
                  x: 250 / 2,
                  y: 150 / 2
                });
              init.call(view.drag);
            });

          card.select("text")
            .text(this.getter("name"));

          card.exit().remove();

          card.each(function(d){
            d.x = d.x ? new Date(d.x) : view.scales.x.domain()[0];
          });

          return this.positionCards();
        }
      });

      return {
        "HorizonsView": HorizonsView
      };
    }
  );

})();
