return {
  {
    "nvim-telescope/telescope.nvim",
    branch = "0.1.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      {
        "nvim-telescope/telescope-fzf-native.nvim",
        build = "make",
        cond = function()
          return vim.fn.executable("make") == 1
        end,
      },
      "nvim-tree/nvim-web-devicons",
    },
    keys = {
      { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "[F]ind [F]iles" },
      { "<leader>fg", "<cmd>Telescope live_grep<cr>", desc = "[F]ind [G]rep" },
      { "<leader>fb", "<cmd>Telescope buffers<cr>", desc = "[F]ind [B]uffers" },
      { "<leader>fh", "<cmd>Telescope help_tags<cr>", desc = "[F]ind [H]elp" },
      { "<leader>fr", "<cmd>Telescope oldfiles<cr>", desc = "[F]ind [R]ecent" },
      { "<leader>fd", "<cmd>Telescope diagnostics<cr>", desc = "[F]ind [D]iagnostics" },
      { "<leader>fs", "<cmd>Telescope lsp_document_symbols<cr>", desc = "[F]ind [S]ymbols" },
      { "<leader>fw", "<cmd>Telescope grep_string<cr>", desc = "[F]ind [W]ord" },
      { "<leader>gc", "<cmd>Telescope git_commits<cr>", desc = "[G]it [C]ommits" },
      { "<leader>gs", "<cmd>Telescope git_status<cr>", desc = "[G]it [S]tatus" },
      { "<leader>/", function()
        require("telescope.builtin").current_buffer_fuzzy_find(require("telescope.themes").get_dropdown({
          winblend = 10,
          previewer = false,
        }))
      end, desc = "Fuzzy search in current buffer" },
    },
    config = function()
      local telescope = require("telescope")
      local actions = require("telescope.actions")
      
      telescope.setup({
        defaults = {
          mappings = {
            i = {
              ["<C-j>"] = actions.move_selection_next,
              ["<C-k>"] = actions.move_selection_previous,
              ["<C-q>"] = actions.send_selected_to_qflist + actions.open_qflist,
              ["<esc>"] = actions.close,
            },
          },
          file_ignore_patterns = {
            "node_modules",
            ".git/",
            "__pycache__",
            "%.cache",
          },
        },
        pickers = {
          find_files = {
            hidden = true,
            follow = true,
          },
          live_grep = {
            additional_args = function()
              return { "--hidden" }
            end,
          },
        },
      })
      
      pcall(telescope.load_extension, "fzf")
    end,
  },
}
