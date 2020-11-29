# README

ベラジョンカジノの取引ログを収集します。

## Usage

1. set_login_data()でメアドとパスを設定
2. download()でダウンロード
3. export()でcsvにエクスポート

## Options

### set_login_data()

set_login_data(メアド, パスワード)
でメアドとパスワードを設定

### download()

download(mode, term_from, term_to)

#### mode

- None -> 1day
- "7days" -> 7days
- "custom" -> term_from, term_toの設定が必要

#### termの書式

mm/dd/yyyy形式で書きます。
例：01/21/2020

### export()

ファイル名を指定してcsvエクスポート

export(ファイル名)