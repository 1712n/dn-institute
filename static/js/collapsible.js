/**
 * @name     liteCollapsible
 * @desc     Make elements collapsible and interactive. 
 * @author   Daniel Souza <daniel@posix.dev.br>
 * @version  2.2
 * @license  MIT
 */

/* ARIA attributes of the control element should be managed exclusively by the
 * script as it isn't relevant when scripting is disabled.
 *
 * The 'hidden' global attribute is generally enough to hide an element and is the default.
 *
 * If element has the 'display' property set it will require 'display: none' to be hidden.
 * 
 * 'visibility: hidden' property is a way to hide an element without causing a layout reflow.
 */

export default class Collapsible {
  constructor(opts) {
    this.debug = opts.debug
    this.control = opts.control
    this.target = opts.target

    if (opts.debug)
      console.log(`constructor; control: ${this.control}; target: ${this.target}`)

    if (this.control === null)
      throw new Error("Control element is null");

    if (this.target === null)
      throw new Error("Target element is null");

    if (opts.aria)
      this.setAria(opts.aria)

    this.control.addEventListener("click", () => {
      this.dispatch("toggle")

      if (this.control.getAttribute("aria-expanded") === "true")
        this.control.setAttribute("aria-expanded", "false")
      else
        this.control.setAttribute("aria-expanded", "true")
    })
  }

  setAria(aria) {
    if (aria.expanded)
      this.control.setAttribute("aria-expanded", "true")
    else
      this.control.setAttribute("aria-expanded", "false")

    if (aria.controls) {
      const target = (this.target.length) ? this.target[0] : this.target
      this.control.setAttribute("aria-controls", target.element.id)
    }
  }

  dispatch(func) {
    if (this.target.length)
      this.target.forEach(item => this[func](item))
    else
      this[func](this.target)
  }

  toggle(item) {
    if (this.isVisible(item.element))
      this.hide(item)
    else
      this.show(item)
  }

  hide(item) {
    if (this.debug)
      console.log(`action: hide; id: ${item.element.id}; class: ${item.element.class}`)

    // 'hidden' remove from layout
    if (!item.visibility) {
      item.element.hidden = true 

    } else {
      item.element.style.opacity = 0
      item.element.style.visibility = item.visibility
    }

    if (item.display)
      item.element.style.display = "none"
  }

  show(item) {
    if (this.debug == true)
      console.log(`action: show; id: ${item.element.id}; class: ${item.element.class}`)

    if (!item.visibility) {
      item.element.hidden = false
    
    } else {
      item.element.style.opacity = 1
      item.element.style.visibility = "visible"
    }

    if (item.display)
      item.element.style.display = item.display
  }

  isVisible(element) {
    if (element.hidden)
      return (!element.hidden)

    if (element.style.visibility)
      return (element.style.visibility == "visible")

    const rect = element.getBoundingClientRect()
    return (rect.height + rect.width > 0)  // visible if it has size 
  }
}
