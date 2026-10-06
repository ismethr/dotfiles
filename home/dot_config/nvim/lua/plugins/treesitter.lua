return {
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPost", "BufNewFile" },
    dependencies = {
      "nvim-treesitter/nvim-treesitter-textobjects",
    },
    config = function()
      require("nvim-treesitter.config").setup({
        install_dir = vim.fs.joinpath(vim.fn.stdpath("data"), "site"),
      })

      local parsers = {
        "bash", "c", "cpp", "css", "dockerfile", "gitignore", "go",
        "html", "java", "javascript", "json", "lua", "markdown",
        "markdown_inline", "python", "rust", "toml", "tsx",
        "typescript", "vim", "vimdoc", "yaml",
      }

      local installed = require("nvim-treesitter.config").get_installed()
      local installed_set = {}
      for _, p in ipairs(installed) do
        installed_set[p] = true
      end

      local to_install = {}
      for _, p in ipairs(parsers) do
        if not installed_set[p] then
          table.insert(to_install, p)
        end
      end

      if #to_install > 0 then
        require("nvim-treesitter.install").install(to_install, { summary = true })
      end
    end,
  },
}
