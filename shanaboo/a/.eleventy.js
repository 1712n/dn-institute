module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addWatchTarget("src/css");

  return {
    dir: {
      input: "src/site",
      output: "_site",
    },
  };
};