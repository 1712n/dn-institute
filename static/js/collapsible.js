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

    this.control.addEventListener('click', this.toggle.bind(this));
  }

  toggle() {
    if (this.target.classList.contains('hidden')) {
      this.target.classList.remove('hidden');
      this.control.setAttribute('aria-expanded', 'true');
    } else {
      this.target.classList.add('hidden');
      this.control.setAttribute('aria-expanded', 'false');
    }
  }
}