(() => {

  class Chart {
    duration = 600
    width = NaN
    height = 500
    margin = {
        top: 10,
        right: 50,
        bottom: 30,
        left: 50
    }

    constructor (container) {
      // Determine width of Chart based on container element
      this.width = parseInt(
        container.style('width')
      )

      this.svg = container.append('svg')
        .attr('class', 'mx-3 my-5')
        .attr('width', this.width)
        .attr('height', this.height)
    }

    draw (data, first) {
      const xScaleFn = d3.scaleBand()
        .domain(['6:00', '7:00', '8:00', '9:00'])
        .range([this.margin.left, this.width - this.margin.right])
        .padding(0.667)

      const yScaleFn = d3.scaleLinear()
        .domain(data)
        .rangeRound([this.height - this.margin.bottom, this.margin.top])

      const xAxisFn = d3.axisBottom()
        .scale(xScaleFn)
        .tickValues(xScaleFn.domain())
        .tickSizeOuter(0)

      const yAxisFn = d3.axisLeft()
        .scale(yScaleFn)
        .ticks(6)
        .tickSizeOuter(0)

      if (first) {
        // Create elements for x and y axis
        this.xAxisElem = this.svg.append('g')
          .attr('transform', `translate(0,${this.height - this.margin.bottom})`)
          .call(xAxisFn)
        this.yAxisElem = this.svg.append('g')
          .attr('transform', `translate(${this.margin.left},0)`)
          .call(yAxisFn)
      } else {
        const t = this.svg
          .transition()
          .duration(this.duration)
        // Transition existing elements
        this.xAxisElem
          .transition(t)
          .call(xAxisFn)
        this.yAxisElem
          .transition(t)
          .call(yAxisFn)
      }
    }
  }

  class Form {

    constructor (container, chart) {
      this.chart = chart

      // Fetch new data any time a button is clicked
      container.selectAll('.btn-check').on('click', () => {
        this.fetch()
      })
    }

    fetch (first=false) {
      const location = container.select('[name="location"]:checked').node().id
      const weekday = container.select('[name="weekday"]:checked').node().id

      // TODO: make actual request
      console.log(location, weekday)
      const data = [0, Math.floor(Math.random() * 200 + 50)]

      this.chart.draw(data, first)
    }

  }

  // Select container element on page
  const container = d3.select('#container')

  // Create Chart and Form objects
  const chart = new Chart(container)
  const form = new Form(container, chart)

  // Load data for the first time
  form.fetch(first=true)

})()