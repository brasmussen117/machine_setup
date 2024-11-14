-- Lazy Neovim Plugin Manager
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
	-- Plugins
	-- { import = "user.plugins_notvscode", cond = (function() return not vim.g.vscode end) },
	-- { import = "user.plugins_always",    cond = true },
	-- { import = "user.plugins_vscode",    cond = (function() return vim.g.vscode end) },
        -- {
        -- 	"unblevable/quick-scope",
        -- 	config = function()
        -- 		vim.cmd("highlight QuickScopePrimary guifg='#afff5f' gui=underline ctermfg=155 cterm=underline")
        -- 		vim.cmd("highlight QuickScopeSecondary guifg='#5fffff' gui=underline ctermfg=81 cterm=underline")
        -- 	end
        -- },
	"xiyaowong/fast-cursor-move.nvim",
	"easymotion/vim-easymotion",
	"tpope/vim-surround",
	"tpope/vim-repeat",
	"folke/which-key.nvim",
	"tjdevries/colorbuddy.nvim",
	{
		"marko-cerovac/material.nvim",
		lazy=false,
		priority=1000,
		config = function()
			vim.g.material_style = "palenight"
		end,
	},
})

-- settings recommended from neovim docs
-- https://neovim.io/doc/user/nvim.html#nvim-from-vim
-- Converted from .vim to .lua by ChatGPT

-- Set runtimepath
-- vim.opt.runtimepath:prepend("~/.vim")
-- vim.opt.runtimepath:append("~/.vim/after")

-- Source vimrc
-- vim.cmd("source ~/.vimrc")

-- Custom Key Mappings

-- Global
vim.g.mapleader = " "

-- Easy-Motion
-- <Leader>f{char} to move to {char}
vim.api.nvim_set_keymap('n', '<Leader><Leader>f', '<Plug>(easymotion-bd-f)', {})
vim.api.nvim_set_keymap('n', '<Leader><Leader>f', '<Plug>(easymotion-overwin-f)', { noremap = true })

-- s{char}{char} to move to {char}{char}
vim.api.nvim_set_keymap('n', '<Leader>s', '<Plug>(easymotion-overwin-f2', { noremap = true})

-- Move to line
vim.api.nvim_set_keymap('n', '<Leader><Leader>L', '<Plug>(easymotion-bd-jk)', {})
vim.api.nvim_set_keymap('n', '<Leader><Leader>L', '<Plug>(easymotion-overwin-line)', { noremap = true })

-- Move to word
vim.api.nvim_set_keymap('n', '<Leader><Leader>w', '<Plug>(easymotion-bd-w)', {})
vim.api.nvim_set_keymap('n', '<Leader><Leader>w', '<Plug>(easymotion-overwin-w)', { noremap = true })

-- boole.nvim setup (https://github.com/nat-418/boole.nvim)
require('boole').setup({
  mappings = {
    increment = '<C-a>',
    decrement = '<C-x>'
  },
  -- User defined loops
  additions = {
    {'Foo', 'Bar'},
    {'tic', 'tac', 'toe'}
  },
  allow_caps_additions = {
    {'enable', 'disable'}
    -- enable → disable
    -- Enable → Disable
    -- ENABLE → DISABLE
  }
})

