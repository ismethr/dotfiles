return {
  {
    "nvim-treesitter/nvim-treesitter-textobjects",
    branch = "main",
    event = { "BufReadPost", "BufNewFile" },
    config = function()
      require("nvim-treesitter-textobjects").setup({
        select = {
          lookahead = true,
        },
        move = {
          set_jumps = true,
        },
      })

      local select = require("nvim-treesitter-textobjects.select").select_textobject
      local move = require("nvim-treesitter-textobjects.move")

      vim.keymap.set({ "x", "o" }, "aa", function() select("@parameter.outer", "textobjects") end, { desc = "around argument" })
      vim.keymap.set({ "x", "o" }, "ia", function() select("@parameter.inner", "textobjects") end, { desc = "inner argument" })
      vim.keymap.set({ "x", "o" }, "af", function() select("@function.outer", "textobjects") end, { desc = "around function" })
      vim.keymap.set({ "x", "o" }, "if", function() select("@function.inner", "textobjects") end, { desc = "inner function" })
      vim.keymap.set({ "x", "o" }, "ac", function() select("@class.outer", "textobjects") end, { desc = "around class" })
      vim.keymap.set({ "x", "o" }, "ic", function() select("@class.inner", "textobjects") end, { desc = "inner class" })

      vim.keymap.set({ "n", "x", "o" }, "]m", function() move.goto_next_start("@function.outer", "textobjects") end, { desc = "Next function start" })
      vim.keymap.set({ "n", "x", "o" }, "]]", function() move.goto_next_start("@class.outer", "textobjects") end, { desc = "Next class start" })
      vim.keymap.set({ "n", "x", "o" }, "]M", function() move.goto_next_end("@function.outer", "textobjects") end, { desc = "Next function end" })
      vim.keymap.set({ "n", "x", "o" }, "][", function() move.goto_next_end("@class.outer", "textobjects") end, { desc = "Next class end" })
      vim.keymap.set({ "n", "x", "o" }, "[m", function() move.goto_prev_start("@function.outer", "textobjects") end, { desc = "Prev function start" })
      vim.keymap.set({ "n", "x", "o" }, "[[", function() move.goto_prev_start("@class.outer", "textobjects") end, { desc = "Prev class start" })
      vim.keymap.set({ "n", "x", "o" }, "[M", function() move.goto_prev_end("@function.outer", "textobjects") end, { desc = "Prev function end" })
      vim.keymap.set({ "n", "x", "o" }, "[]", function() move.goto_prev_end("@class.outer", "textobjects") end, { desc = "Prev class end" })
    end,
  },
}
